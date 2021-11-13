from datetime import datetime

import psutil
from memory_profiler import memory_usage

from utils.helper import get_logger

_logger = get_logger('measure')


def memory_usage_tracking(method):
    def measure_task(*args, **kwargs):
        start_time_of_task = datetime.now()
        _logger.info(f'start tracking memory info at {start_time_of_task} ')
        mem_usage, result = memory_usage(
            (method, args, kwargs), retval=True, max_usage=True)

        end_time_of_task = datetime.now()

        run_time = (end_time_of_task - start_time_of_task).total_seconds() / 60
        _logger.info(f'completed in {run_time} minutes with max mem: {mem_usage} MB')


        return result

    return measure_task


def track_cpu_usage():
    cpu_dict = { "cpu_percent" : psutil.cpu_percent(interval=None, percpu=True),
                 "cpu_freq": psutil.cpu_freq(),
                 "cpu_load_avg": [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]}

    return cpu_dict



