from fastapi.testclient import TestClient
from label_api import app

class TestAPIs(object):
    client = TestClient(app)

    def test_create(self):
        response = self.client.post("/api/tasks/",
                                    json={
                                        "do_label_task": False,
                                        "do_prod_generate_task": True,
                                        "model_type": "keyword_model",
                                        "predict_type": "author_name",
                                        "start_time": "2020-01-01 00:00:00",
                                        "end_time": "2020-12-31 23:59:59",
                                        "target_schema": "wh_bbs_01",
                                        "target_table": "ts_page_content",
                                        "date_info": True,
                                        "queue_name": "queue1",
                                        "prod_generate_config": {
                                            "prod_generate_schedule": "2021-11-02 11:22:00",
                                            "prod_generate_task_id": "string",
                                            "prod_generate_schema": "audience_result",
                                            "prod_generate_target_table": "ts_page_content",
                                            "prod_generate_table": "string",
                                            "prod_generate_date_info": True,
                                            "prod_generate_start_time": "2020-01-01 00:00:00",
                                            "prod_generate_end_time": "2020-12-31 23:59:59",
                                            "prod_generate_queue_name": "queue1"
                                          }
                                        })
        assert response.status_code == 200

    def test_task_list(self):
        response = self.client.get("/api/tasks/")
        assert response.status_code == 200

    def test_check_status(self):
        response = self.client.get(f"/api/tasks/e138514e307a11eca07b04ea56825bad")
        assert response.status_code == 200

    def test_sample_result(self):
        response = self.client.get(f"/api/tasks/e138514e307a11eca07b04ea56825bad/sample/?table_name=wh_panel_mapping_Dcard&table_name=wh_panel_mapping_forum")
        assert response.status_code == 200







