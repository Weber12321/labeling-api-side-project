from typing import List, Union
import pandas as pd
from sqlalchemy import create_engine

from settings import DatabaseConfig
from utils.database_core import connect_database, get_result_query, to_dataframe, create_table, drop_table
from utils.helper import get_logger


def scrap_result(_id: str, table_name: str) -> pd.DataFrame:
    connection = connect_database(schema=DatabaseConfig.OUTPUT_SCHEMA, output=True)
    q = get_result_query(_id, table_name)
    with connection.cursor() as cursor:
        cursor.execute(q)
        results = to_dataframe(cursor.fetchall())
        connection.close()
    return results

def clean_data(df: pd.DataFrame) -> Union[pd.DataFrame, None]:
    group = df.groupby(['source_author', 'panel']).size().reset_index(name='counts')
    duplicated_author = group.loc[group.source_author.duplicated() == True]

    if duplicated_author.empty:
        return

    iter_item = group[group.duplicated(['source_author'])]['source_author'].to_list()
    delete_dict = {}
    for i in iter_item:
        temp = group[group.source_author == i]
        if temp.counts.iloc[0] > temp.counts.iloc[1]:
            delete_dict.update({temp.iloc[1, 0]: temp.iloc[1, 1]})
        elif temp.counts.iloc[0] < temp.counts.iloc[1]:
            delete_dict.update({temp.iloc[0, 0]: temp.iloc[0, 1]})
        else:
            pass

    for k, v in delete_dict.items():
        group = group[~((group.source_author.isin([k])) & (group.panel.isin([v])))]
    return group

def run_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    remove_duplicates_df = clean_data(df) if clean_data(df) else None
    uniq_df = df.sort_values(by='create_time').drop_duplicates(subset=['source_author', 'panel'], keep='last')

    if not remove_duplicates_df:
        return uniq_df

    output = pd.merge(uniq_df, remove_duplicates_df, on=['source_author', 'panel']).drop(['counts'], axis=1)

    return output.sort_values(by='create_time')

def write_results_back_to_database(df: pd.DataFrame ,table_name: str, logger: get_logger):


    create_table(table_name, logger, schema=DatabaseConfig.OUTPUT_SCHEMA)

    engine = create_engine(DatabaseConfig.OUTPUT_ENGINE_INFO, pool_size=0, max_overflow=-1)
    connection = engine.connect()

    _table_name = f'wh_panel_mapping_{table_name}'
    df.to_sql(name=_table_name, con=connection, if_exists='append', index=False)
    return _table_name

def run_workflow(task_id: str, target_table: List[str], logger: get_logger, drop = False):
    output_list = []
    for i in target_table:
        try:
            logger.info(f'task {task_id} start cleaning the data from table {i}... ')
            scrap_df = scrap_result(task_id, i)
            output = run_cleaning(scrap_df)
        except Exception as e:
            err_meg = f'task {task_id} failed to clean the data from table {i}, ' \
                      f'additional error message {e}'
            logger.error(err_meg)
            raise err_meg

        try:
            final_table_name = write_results_back_to_database(output, i, logger)
            output_list.append(final_table_name)
        except Exception as e:
            err_meg = f'task {task_id} failed to write results, ' \
                      f'additional error message {e}'
            logger.error(err_meg)
            raise err_meg

    if drop:
        for table in target_table:
            drop_table(table, logger, schema='audience_result')


    return {task_id: output_list}

