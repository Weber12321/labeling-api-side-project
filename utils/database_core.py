import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

import pymysql
import pandas as pd
from sqlmodel import SQLModel, create_engine
from sqlalchemy import create_engine as C

from utils.helper import get_logger
from settings import DatabaseConfig


def create_db(db_path, config_db):
    if os.path.exists(f'../{db_path}'):
        pass
    else:
        engine = create_engine(f'{config_db}', encoding='utf-8')
        SQLModel.metadata.create_all(engine)

def connect_database(schema = None, output = False):
    if not output:
        _config = {
            'host': DatabaseConfig.INPUT_HOST,
            'port': DatabaseConfig.INPUT_PORT,
            'user': DatabaseConfig.INPUT_USER,
            'password': DatabaseConfig.INPUT_PASSWORD,
            'db': schema,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
    else:
        _config = {
            'host': DatabaseConfig.OUTPUT_HOST,
            'port': DatabaseConfig.OUTPUT_PORT,
            'user': DatabaseConfig.OUTPUT_USER,
            'password': DatabaseConfig.OUTPUT_PASSWORD,
            'db': schema,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
    try:
        connection = pymysql.connect(**_config)
        return connection

    except Exception as e:
        logging.error('Fail to connect to database.')
        raise e


def to_dataframe(data):
    return pd.DataFrame.from_dict(data)

def scrap_data_to_dict(query: str, schema: str):
    connection = connect_database(schema=schema, output=True)
    cur = connection.cursor()
    cur.execute(query)
    result = cur.fetchall()
    connection.close()
    return result



# def get_label_data_count(task_id):
#     connection = C(Database.OUTPUT_ENGINE_INFO).connect()
#     q = f'SELECT length_output_table FROM state where task_id = "{task_id}";'
#     _count = connection.execute(q).fetchone()[0]
#     connection.close()
#     return _count


# def get_data_by_batch(count, predict_type, batch_size,
#                       schema, table, date_info = False, **kwargs) -> pd.DataFrame:
#
#     if not date_info:
#         # if not chunk_by_source:
#         for offset in range(0, count, batch_size):
#             func = connect_database
#             with func(schema=schema).cursor() as cursor:
#                 q = f"SELECT * FROM {table} " \
#                     f"WHERE {predict_type} IS NOT NULL " \
#                     f"LIMIT {batch_size} OFFSET {offset}"
#                 cursor.execute(q)
#                 result = to_dataframe(cursor.fetchall())
#                 yield result
#                 func(schema=schema).close()
#
#     else:
#         # if not chunk_by_source:
#         for offset in range(0, count, batch_size):
#             func = connect_database
#             with func(schema=schema).cursor() as cursor:
#                 q = f"SELECT * FROM {table} " \
#                     f"WHERE {predict_type} IS NOT NULL " \
#                     f"AND post_time >= '{kwargs.get('start_time')}' " \
#                     f"AND post_time <= '{kwargs.get('end_time')}' "\
#                     f"LIMIT {batch_size} OFFSET {offset}"
#                 cursor.execute(q)
#                 result = to_dataframe(cursor.fetchall())
#                 yield result
#                 func(schema=schema).close()



def create_table(table_ID: str, logger: get_logger, schema=None):
    insert_sql = f'CREATE TABLE IF NOT EXISTS `{table_ID}`(' \
                 f'`id` VARCHAR(32) NOT NULL,' \
                 f'`task_id` VARCHAR(32) NOT NULL,' \
                 f'`source_author` TEXT(65535) NOT NULL,' \
                 f'`panel` VARCHAR(200) NOT NULL,' \
                 f'`create_time` DATETIME NOT NULL,' \
                 f'`field_content` TEXT(65535) NOT NULL,' \
                 f'`match_content` TEXT(1073741823) NOT NULL' \
                 f')ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ' \
                 f'AUTO_INCREMENT=1 ;'
    func = connect_database
    try:
        with func(schema, output=True).cursor() as cursor:
            logger.info('connecting to database...')
            logger.info('creating table...')
            cursor.execute(insert_sql)
            func(schema, output=True).close()
            logger.info(f'successfully created table {table_ID}')
    except Exception as e:
        logger.error(e)
        raise e


def create_state_table(logger: get_logger, schema=None):
    insert_sql = f'CREATE TABLE IF NOT EXISTS `state`(' \
                 f'`task_id` VARCHAR(32) NOT NULL,' \
                 f'`stat` VARCHAR(32) NOT NULL,' \
                 f'`prod_stat` VARCHAR (10),' \
                 f'`model_type` VARCHAR(32) NOT NULL,' \
                 f'`predict_type` VARCHAR(32) NOT NULL,' \
                 f'`date_range` TEXT(1073741823),' \
                 f'`target_table` VARCHAR(32) NOT NULL,' \
                 f'`create_time` DATETIME NOT NULL,' \
                 f'`peak_memory` FLOAT(10),' \
                 f'`length_receive_table` INT(11),' \
                 f'`length_output_table` INT(11),' \
                 f'`length_prod_table` VARCHAR (100),' \
                 f'`result` TEXT(1073741823),' \
                 f'`uniq_source_author` VARCHAR(100),' \
                 f'`rate_of_label` INT(11),' \
                 f'`run_time` FLOAT(10),' \
                 f'`check_point` DATETIME' \
                 f')ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ' \
                 f'AUTO_INCREMENT=1 ;'
    func = connect_database
    try:
        with func(schema, output=True).cursor() as cursor:
            logger.info('connecting to database...')
            logger.info('creating table...')
            cursor.execute(insert_sql)
            func(schema, output=True).close()
            logger.info(f'successfully created table.')
    except Exception as e:
        logger.error(e)
        raise e



def insert2state(task_id, status, model_type, predict_type,
                 date_range, target_table, time, result,
                 logger: get_logger, schema=None):

    connection = connect_database(schema=schema, output=True)

    insert_sql = f'INSERT INTO state ' \
                 f'(task_id, stat, model_type, predict_type, date_range, target_table, create_time, result) ' \
                 f'VALUES (' \
                 f'"{task_id}", ' \
                 f'"{status}", ' \
                 f'"{model_type}", ' \
                 f'"{predict_type}", ' \
                 f'"{date_range}", ' \
                 f'"{target_table}", ' \
                 f'"{time}", ' \
                 f'"{result}");'
    try:
        cursor = connection.cursor()
        logger.info('connecting to database...')
        cursor.execute(insert_sql)
        logger.info(f'successfully insert state into table.')
        connection.commit()
        connection.close()
    except Exception as e:
        raise e

def update2state(task_id, result, logger: get_logger, input_row_length = None,
                 output_row_length = None, run_time=None, schema=None, success=True,
                 check_point=None, uniq_source_author=None):

    connection = connect_database(schema=schema, output=True)
    if success:
        insert_sql = f'UPDATE state ' \
                     f'SET stat = "SUCCESS", result = "{result}", ' \
                     f'uniq_source_author = "{uniq_source_author}", ' \
                     f'length_receive_table = {input_row_length}, ' \
                     f'length_output_table = {output_row_length}, ' \
                     f'run_time = {run_time} ' \
                     f'where task_id = "{task_id}"'
    else:
        insert_sql = f'UPDATE state ' \
                     f'SET stat = "FAILURE", result = "{result}", check_point = "{check_point}" ' \
                     f'where task_id = "{task_id}"'


    try:
        cursor = connection.cursor()
        logger.info('connecting to database...')
        cursor.execute(insert_sql)
        logger.info(f'successfully write state into table.')
        connection.commit()
        connection.close()
    except Exception as e:
        raise e


def drop_table(table_name: str, logger: get_logger, schema=None) :
    """drop table name"""
    drop_sql = f'DROP TABLE {table_name};'
    func = connect_database
    try:
        with func(schema=schema, output=True).cursor() as cursor:
            logger.info('connecting to database...')
            logger.info('dropping table...')
            cursor.execute(drop_sql)
            func(schema=schema, output=True).close()
            logger.info(f'successfully dropped table {table_name}')
    except Exception as e:
        logger.error('Cannot drop the table')
        raise e


def get_create_task_query(target_table, predict_type, start_time, end_time, get_all = False):

    if not get_all:
        q = f"SELECT * FROM {target_table} " \
            f"WHERE {predict_type} IS NOT NULL " \
            f"AND post_time >= '{start_time}'" \
            f"AND post_time <= '{end_time}'"
    else:
        q = f"SELECT * FROM {target_table} " \
            f"WHERE {predict_type} IS NOT NULL"

    return q

def get_count_query():
    return 'SELECT COUNT(task_id) FROM celery_taskmeta'

def get_tasks_query_recent(order_column, number):
    q = f'SELECT * FROM state ' \
        f'ORDER BY {order_column} DESC ' \
        f'LIMIT {number} '
    schema = DatabaseConfig.OUTPUT_SCHEMA
    connection = connect_database(schema, output=True)
    cur = connection.cursor()
    # cursor.executescript(sql_as_string)
    cur.execute(q)
    r = cur.fetchall()
    connection.close()
    return r

def get_table_info(id):
    q = f"""SELECT result 
    FROM state WHERE 
    task_id = '{id}'
    """
    connection = connect_database(schema=DatabaseConfig.OUTPUT_SCHEMA, output=True)
    cur = connection.cursor()
    cur.execute(q)
    result = cur.fetchone()
    return result.get('result').split(',')


def get_sample_query(_id, tablename, number):
    q = f"(SELECT * FROM {tablename} WHERE task_id = '{_id}' " \
        f"AND rand() <= 0.2 " \
        f"LIMIT {number})"
    return q

def query_state_by_id(_id):
    q = f"SELECT * FROM state WHERE task_id = '{_id}'"
    schema = DatabaseConfig.OUTPUT_SCHEMA
    connection = connect_database(schema, output=True)
    cur = connection.cursor()
    # cursor.executescript(sql_as_string)
    cur.execute(q)
    r = cur.fetchone()
    connection.close()
    return r


def get_result_query(_id, tablename):
    q = f"SELECT * FROM {tablename} WHERE task_id = '{_id} '"
    return q

def add_column(schema, table, col_name, col_type, **kwargs):

    if kwargs:
        condition = ''
        for k,v in kwargs.items():
            condition += f' {k} {v}'
    else:
        condition = ''
    connection = connect_database(schema=schema, output=True)
    q = f'ALTER TABLE {table} ' \
        f'ADD COLUMN {col_name} {col_type}'

    q += condition
    with connection.cursor() as cursor:
        cursor.execute(q)
        connection.close()

def get_distinct_count(schema, tablename, condition=None, start_time=None, end_time=None):
    info = f"mysql+pymysql://{os.getenv('INPUT_USER')}:{os.getenv('INPUT_PASSWORD')}@" \
           f"{os.getenv('INPUT_HOST')}:{os.getenv('INPUT_PORT')}/{schema}?charset=utf8mb4"
    connection = C(info).connect()
    # if date_info:
    if not connection:
        q = f'SELECT count(distinct s_id, author) ' \
            f'FROM {tablename} ' \
            f'WHERE author IS NOT NULL ' \
            f'AND s_id IS NOT NULL ' \
            f"AND post_time >= '{start_time}' " \
            f"AND post_time <= '{end_time}';"
    else:
        q = f'SELECT count(distinct s_id, author) ' \
            f'FROM {tablename} ' \
            f'WHERE author IS NOT NULL ' \
            f'AND s_id IS NOT NULL ' \
            f'AND s_id in {condition} ' \
            f"AND post_time >= '{start_time}' " \
            f"AND post_time <= '{end_time}';"
    # else:
    #     if not connection:
    #         q = f'SELECT count(distinct s_id, author) ' \
    #             f'FROM {tablename} ' \
    #             f'WHERE author IS NOT NULL and s_id IS NOT NULL;'
    #     else:
    #         q = f'SELECT count(distinct s_id, author) ' \
    #             f'FROM {tablename} ' \
    #             f'WHERE author IS NOT NULL and s_id IS NOT NULL ' \
    #             f'and s_id in {condition};'
    count = connection.execute(q).fetchone()[0]
    connection.close()

    return count

def get_label_source_from_state(task_id):
    connection = C(DatabaseConfig.OUTPUT_ENGINE_INFO).connect()
    q = f'SELECT target_table FROM state WHERE task_id = "{task_id}"; '
    source_name = connection.execute(q).fetchone()[0]
    connection.close()

    return source_name


def get_timedelta_query(predict_type, table, start_time, end_time):
    q = f"SELECT * FROM {table} " \
        f"WHERE {predict_type} IS NOT NULL " \
        f"AND post_time >= '{start_time}' " \
        f"AND post_time <= '{end_time}';"

    return q

def get_batch_by_timedelta(schema, predict_type, table,
                           begin_date: datetime, last_date: datetime,
                           interval: timedelta = timedelta(hours=6)):
    while begin_date <= last_date:

        connection = connect_database(schema=schema)

        if begin_date + interval > last_date:
            break

        else:
            start_date_interval = begin_date + interval
            cursor = connection.cursor()
            cursor.execute(get_timedelta_query(predict_type, table, begin_date, start_date_interval))
            result = to_dataframe(cursor.fetchall())
            begin_date += interval

            yield result, begin_date
            connection.close()


def check_state_result_for_task_info(task_id: str, schema: str):
    connection = connect_database(schema=schema, output=True)
    sql = f"""select result,rate_of_label from state where task_id = "{task_id}";"""

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    connection.close()

    if ',' in result.get('result'):
        return result.get('rate_of_label')
    else:
        return None

def check_state_prod_length_for_task_info(task_id: str, schema: str):
    connection = connect_database(schema=schema, output=True)
    sql = f"""select result,length_prod_table from state where task_id = "{task_id}";"""

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    connection.close()

    if ',' in result.get('result'):
        return result.get('length_prod_table')
    else:
        return None


def check_state_exist(logger):
    engine = create_engine(DatabaseConfig.OUTPUT_ENGINE_INFO).connect()
    _exist_tables = [i[0] for i in engine.execute('SHOW TABLES').fetchall()]
    if 'state' not in _exist_tables:
        create_state_table(logger, schema=DatabaseConfig.OUTPUT_SCHEMA)
    engine.close()

def alter_column_type(schema: str, table_name: str, column_name: str, datatype: str) -> None:
    q = f"""ALTER TABLE {table_name} MODIFY {column_name} {datatype};"""
    connection = connect_database(schema, output=True)
    cur = connection.cursor()
    cur.execute(q)
    connection.close()



