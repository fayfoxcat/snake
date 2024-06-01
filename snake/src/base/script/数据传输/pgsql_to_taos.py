import time
from datetime import timedelta, datetime

import psycopg2
import taosrest
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库连接信息
pg_config = {
    'host': '172.18.37.208',
    'port': 5432,
    'dbname': 'envs-bak',
    'user': 'postgres',
    'password': 'postgres'
}

# TAOS 数据库连接信息
taos_config = {
    'host': '172.18.37.208',
    'user': 'root',
    'password': 'taosdata',
    'database': 'elss'
}

# 最大重试次数
MAX_RETRIES = 5
RETRY_DELAY = 5  # 秒

# 使用 psycopg2 连接 PostgreSQL 并查询数据
def fetch_pg_data(start_date, end_date):
    conn = None
    cursor = None
    retries = 0
    while retries < MAX_RETRIES:
        try:
            conn = psycopg2.connect(**pg_config)
            cursor = conn.cursor()
            query = f"""SELECT time_point, measured_electricity, ultra_10h_predict_electricity,
             ultra_10h_predict_discharge, district_id, station_type FROM discharge_district
             WHERE time_point BETWEEN '{start_date}' AND '{end_date}'
             """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching data from PostgreSQL: {e}")
            retries += 1
            time.sleep(RETRY_DELAY)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return []

# 将数据插入到 TAOS 数据库
def insert_to_taos(data):
    conn = None
    cursor = None
    retries = 0
    while retries < MAX_RETRIES:
        try:
            conn = taosrest.connect(url="http://172.18.37.208:6041", database="elss")
            cursor = conn.cursor()
            for row in data:
                time_point, measured_electricity, predict_electricity, discharge, district_id, station_type = row
                time_point = 'NULL' if time_point is None else f"'{time_point}'"
                measured_electricity = 'NULL' if measured_electricity is None else measured_electricity
                predict_electricity = 'NULL' if predict_electricity is None else predict_electricity
                discharge = 'NULL' if discharge is None else discharge

                create_taos_subtable(cursor, station_type)

                insert_query = f"""
                INSERT INTO discharge_district_10T_0_{station_type} 
                VALUES ({time_point}, {measured_electricity}, {predict_electricity}, {discharge})
                """
                cursor.execute(insert_query)
            conn.commit()
            return
        except Exception as e:
            logging.error(f"Error inserting data to TAOS: {e}")
            retries += 1
            time.sleep(RETRY_DELAY)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# 创建子表
def create_taos_subtable(cursor, station_type):
    create_query = f"""
    CREATE TABLE IF NOT EXISTS discharge_district_10T_0_{station_type} 
    USING discharge_district 
    TAGS ('10T', 0, '{station_type}')
    """
    cursor.execute(create_query)

# 时间区间按月拆分
def split_date_range_by_month(start_date, end_date):
    date_ranges = []
    current_date = start_date

    while current_date < end_date:
        next_month = current_date.replace(day=28) + timedelta(days=4)  # 将日期移到下个月
        next_month = next_month.replace(day=1)  # 设置为下个月的第一天
        last_day_of_month = next_month - timedelta(days=1)  # 找到本月的最后一天

        # 确保结束时间不超过指定的end_date
        if last_day_of_month >= end_date:
            last_day_of_month = end_date - timedelta(days=1)

        date_ranges.append((current_date, last_day_of_month + timedelta(days=1)))
        current_date = next_month

    return date_ranges

# 主函数
def main():
    # 设置开始时间和结束时间
    start_date = datetime(2023, 7, 1)
    end_date = datetime(2023, 8, 1)
    date_ranges = split_date_range_by_month(start_date, end_date)

    # 循环调用 fetch_pg_data 方法并处理异常，将结果插入 taos 数据库
    for start, end in date_ranges:
        try:
            pg_data = fetch_pg_data(start, end)
            if pg_data:
                insert_to_taos(pg_data)
        except Exception as e:
            logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
