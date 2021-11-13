import pandas as pd
from sqlalchemy import create_engine

from settings import DatabaseConfig
from utils.database_core import connect_database, to_dataframe, create_table
from utils.clean_up_result import run_cleaning
from utils.helper import get_logger


class TaskGenerateOutput(object):
    def __init__(self, task_id: str, schema: str, table: str , logger: get_logger):
        self.task_id = task_id
        self.schema = schema
        self.table = table
        # self.data = data
        self.logger = logger

    def clean(self):
        df = self.scrap_success_data_to_df(self.task_id, self.schema, self.table, self.logger)
        _output_df = run_cleaning(df)
        output_table_name, _row_number = self.write_to_output_table(_output_df, self.schema, self.table, self.logger)
        return output_table_name, _row_number

    def scrap_success_data_to_df(self, task_id: str, schema: str, table: str ,logger: get_logger) -> pd.DataFrame:
        logger.info(f'start scraping label data ...')
        _from_success_table = f'SELECT * FROM {table} WHERE task_id = "{task_id}"'
        try:
            connection = connect_database(schema, output=True)
            cursor = connection.cursor()
            cursor.execute(_from_success_table)
            result = to_dataframe(cursor.fetchall())
            connection.close()
            return result
        except Exception as e:
            logger.error(e)
            raise e

    def write_to_output_table(self, df: pd.DataFrame, schema: str, table_name: str, logger):
        # _table_name = f"wh_panel_mapping_{table_name}_production"
        _table_name = f"wh_panel_mapping_{table_name}"
        try:
            _connection = create_engine(DatabaseConfig.OUTPUT_ENGINE_INFO).connect()
            _exist_tables = [i[0] for i in _connection.execute('SHOW TABLES').fetchall()]
            if _table_name not in _exist_tables:
                create_table(_table_name, logger, schema)

            logger.info(f'start writing data into {_table_name}')

            df.to_sql(name=_table_name, con=_connection, if_exists='append', index=False)

            logger.info(f'finish writing data into {_table_name}')

            return _table_name, len(df)

        except Exception as e:
            raise e


