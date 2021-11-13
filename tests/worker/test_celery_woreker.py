import uuid
from datetime import datetime, timedelta
from unittest import TestCase
from celery.utils.debug import sample_mem, memdump
from celery_worker import label_data
from settings import CreateLabelRequestBody
from utils.run_label_task import read_from_dir


class TestCeleryWorker(TestCase):
    create_request_body = CreateLabelRequestBody()

    def test_worker(self):

        task_id = uuid.uuid1().hex
        pattern = read_from_dir(self.create_request_body.model_type, self.create_request_body.predict_type)

        pred_type = "author"
        date_info_dict = {'start_time': self.create_request_body.start_time,
                          'end_time': self.create_request_body.end_time}


        label_data.apply_async(args=(task_id, self.create_request_body.target_schema,
                                      pattern, self.create_request_body.model_type, pred_type),
                                kwargs=date_info_dict,
                                task_id=task_id,
                                expires=datetime.now() + timedelta(days=7))


