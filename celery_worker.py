from typing import List

from dotenv import load_dotenv
from datetime import datetime

from celery import Celery

from settings import DatabaseConfig
from utils.database_core import update2state, get_batch_by_timedelta
from utils.helper import get_logger, get_config
from utils.run_label_task import labeling
from utils.task_generate_production_core import TaskGenerateOutput
from utils.task_info_core import TaskInfo
from utils.worker_core import memory_usage_tracking, track_cpu_usage


configuration = get_config()

celery_app = Celery(name=configuration.CELERY_NAME,
                    backend=configuration.CELERY_BACKEND,
                    broker=configuration.CELERY_BROKER)

celery_app.conf.update(enable_utc=configuration.CELERY_ENABLE_UTC)
celery_app.conf.update(timezone=configuration.CELERY_TIMEZONE)
celery_app.conf.update(result_extended=configuration.CELERY_RESULT_EXTENDED)
celery_app.conf.update(task_track_started=configuration.CELERY_TASK_TRACK_STARTED)


@celery_app.task(name=f'{configuration.CELERY_NAME}.label_data', track_started=True)
# @memory_usage_tracking
def label_data(task_id: str, **kwargs) -> List[str]:
    _logger = get_logger('label_data')
    load_dotenv()
    start_time = datetime.now()
    # cpu_info_df = pd.DataFrame(columns=['task_id', 'batch', 'cpu_percent', 'cpu_freq', 'cpu_load_avg'])

    start_date = kwargs.get('START_TIME')
    end_date = kwargs.get('END_TIME')
    start_date_d = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    end_date_d = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")

    table_dict = {}
    count = 0
    row_number = 0

    for idx, elements in enumerate(get_batch_by_timedelta(kwargs.get('INPUT_SCHEMA'),
                                                         kwargs.get('PREDICT_TYPE'),
                                                         kwargs.get('INPUT_TABLE'),
                                                         start_date_d, end_date_d)):

        _logger.info(f'Start calculating task {task_id} {kwargs.get("INPUT_SCHEMA")}.'
                     f'{kwargs.get("INPUT_TABLE")}_batch_{idx} ...')

        # change the `author` back to `author_name` to fit the label modeling
        pred = "author_name" if kwargs.get('PREDICT_TYPE') == "author" else kwargs.get('PREDICT_TYPE')

        element, date_checkpoint = elements

        if element.empty:
            continue

        count += len(element)

        try:
            _output, row_num = labeling(task_id, element, kwargs.get('MODEL_TYPE'),
                               pred, kwargs.get('pattern'), _logger)

            row_number += row_num

            for k,v in _output.items():
                if table_dict.get(k):
                    table_dict[k] = table_dict.get(k).union(v)
                else:
                    table_dict.update({k:v})


            _logger.info(f'task {task_id} {kwargs.get("INPUT_SCHEMA")}.'
                         f'{kwargs.get("INPUT_TABLE")}_batch_{idx} finished labeling...')

            # cpu_track = track_cpu_usage()
            # cpu_track.update({'task_id': task_id, 'batch': idx})
            # cpu_info_df = cpu_info_df.append(cpu_track, ignore_index=True)

        except Exception as e:
            update2state(task_id, '', _logger,
                         schema=DatabaseConfig.OUTPUT_SCHEMA,
                         success=False,
                         check_point=date_checkpoint)

            err_msg = f'task {task_id} failed at {kwargs.get("INPUT_SCHEMA")}.' \
                      f'{kwargs.get("INPUT_TABLE")}_batch_{idx}, additional error message {e}'
            _logger.error(err_msg)
            raise e

    finish_time = (datetime.now() - start_time).total_seconds() / 60
    _logger.info(f'task {task_id} {kwargs.get("INPUT_SCHEMA")}.'
                 f'{kwargs.get("INPUT_TABLE")} done, total time is '
                 f'{finish_time} minutes')

    update2state(task_id, ','.join(table_dict.keys()), _logger, count, row_number, finish_time,
                 schema=DatabaseConfig.OUTPUT_SCHEMA,
                 uniq_source_author=','.join([str(len(i)) for i in table_dict.values()]))

    # cpu_info_df.to_csv(f'save_file/{task_id}_cpu_info.csv', encoding='utf-8-sig', index=False)

    return list(table_dict.keys())

@celery_app.task(name=f'{configuration.CELERY_NAME}.generate_production', track_started=True)
def generate_production(output_table: List[str], task_id: str, **kwargs) -> None:
    _logger = get_logger('produce_outcome')
    start_time = datetime.now()

    for tb in output_table:
        _logger.info(f'start generating output for table {tb}...')

        generate_production = TaskGenerateOutput(task_id,
                                                 kwargs.get('OUTPUT_SCHEMA'),
                                                 tb, _logger)
        _output_table_name, row_num = generate_production.clean()


        _logger.info(f'finish generating output for table {tb}')
        _logger.info(f'start generating task validation for table {tb} ...')

        task_info_obj = TaskInfo(task_id,
                                 kwargs.get('OUTPUT_SCHEMA'),
                                 tb,
                                 kwargs.get('INPUT_TABLE'),
                                 row_num, _logger)

        _logger.info(f'start calculating rate_of_label for table {tb}...')
        task_info_obj.generate_output()
        _logger.info(f'finish calculating rate_of_label for table {tb}')

        _logger.info(
            f'total time for {task_id}: {tb} is '
            f'{(datetime.now() - start_time).total_seconds() / 60} minutes')

    _logger.info(f'finish task {task_id} generate_production, total time: '
                 f'{(datetime.now() - start_time).total_seconds() / 60} minutes')





