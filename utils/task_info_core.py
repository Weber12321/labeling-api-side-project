from typing import Dict
from utils.database_core import connect_database, get_label_source_from_state, \
    check_state_result_for_task_info, check_state_prod_length_for_task_info
from utils.helper import get_logger


class TaskInfo(object):
    def __init__(self, task_id: str, schema: str, table: str,
                 from_target_table: str, row_count: int,
                 logger: get_logger):
        self.task_id = task_id
        self.schema = schema
        self.table = table
        self.from_target_table = from_target_table
        self.row_count = row_count
        self.logger = logger
        # self.partial_table = table.split("_")[-1]
        self._from_schema = get_label_source_from_state(task_id)



    def generate_output(self):

        _source_distinct_count = self.get_source_distinct_count(self.task_id,
                                                                self.schema,
                                                                self.logger)

        table_source_distinct_count = None
        if ',' in _source_distinct_count.get('uniq_source_author'):
            for idx, item in enumerate(_source_distinct_count.get('result').split(',')):
                if item == self.table:
                    table_source_distinct_count = int(_source_distinct_count.get('uniq_source_author').split(',')[idx])
                else:
                    pass
        else:
            table_source_distinct_count = int(_source_distinct_count.get('uniq_source_author'))

        assert table_source_distinct_count != None , 'table_source_distinct_count cannot be None'

        # generate rate of label for each output table
        rate_of_label = check_state_result_for_task_info(self.task_id, self.schema)
        if rate_of_label:
            new_rate_of_label = rate_of_label + ',' + str(round((self.row_count / table_source_distinct_count)*100, 2))
        else:
            new_rate_of_label = str(round((self.row_count / table_source_distinct_count)*100, 2))

        # generate length of production for each output table
        length_prod_table = check_state_prod_length_for_task_info(self.task_id, self.schema)
        if length_prod_table:
            new_length_prod_table = length_prod_table + ',' + str(self.row_count)
        else:
            new_length_prod_table = str(self.row_count)


        _task_info_statement = {
            'task_id' : self.task_id,
            'length_prod_table' : new_length_prod_table,
            'rate_of_label' : new_rate_of_label
        }

        self.update_task_info(self.schema, self.logger, **_task_info_statement)

    def get_status_info(self, task_id, schema, logger) -> Dict:
        state_query = f'SELECT * FROM state WHERE task_id = "{task_id}"'
        func = connect_database
        try:
            with func(schema, output=True).cursor() as cursor:
                cursor.execute(state_query)
                result = cursor.fetchone()
                func(schema, output=True).close()
                logger.info(f'scrape state info')
                return result
        except Exception as e:
            logger.error(e)
            raise e

    def update_task_info(self, schema, logger, **kwargs):

        task_id = kwargs.get('task_id')
        # input_data_size = kwargs.get('input_data_size')
        length_prod_table = kwargs.get('length_prod_table')
        # max_memory_usage = kwargs.get('max_memory_usage')
        # run_time = kwargs.get('run_time')
        rate_of_label = kwargs.get('rate_of_label')


        update_sql = f'UPDATE state ' \
                     f'SET prod_stat = "finish", ' \
                     f'length_prod_table = "{length_prod_table}", ' \
                     f'rate_of_label = "{rate_of_label}" ' \
                     f'where task_id = "{task_id}"'

        try:
            _connection = connect_database(schema, output=True)
            cursor = _connection.cursor()
            cursor.execute(update_sql)
            _connection.commit()
            _connection.close()
            logger.info(f'successfully write into table state.')

        except Exception as e:
            logger.error(e)
            raise e


    def get_source_distinct_count(self, task_id, schema, logger):

        q = f"""select result,uniq_source_author from state where task_id = "{task_id}";"""

        try:
            _connection = connect_database(schema, output=True)
            cursor = _connection.cursor()
            cursor.execute(q)
            source_distinct_count_str_wiht_result = cursor.fetchone()
            _connection.close()
            logger.info(f'successfully get uniq_source_author number from table state.')

        except Exception as e:
            logger.error(e)
            raise e

        return source_distinct_count_str_wiht_result



