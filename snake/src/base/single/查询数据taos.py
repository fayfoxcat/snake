import taos
import time

def connect_taos():
    conn = taos.connect(host="172.18.37.208", user="root", password="taosdata", database="elss")
    cursor = conn.cursor()
    return conn, cursor

def query_data(station_id, start_time, end_time):
    conn, cursor = connect_taos()
    try:
        # 构建查询语句，使用参数
        query = f"SELECT * FROM agc_telemetry WHERE (station_id IN ({station_id}) AND collect_time >= '{start_time}' AND collect_time < '{end_time}') ORDER BY collect_time ASC;"

        start_query_time = time.time()  # 开始时间
        cursor.execute(query)
        end_query_time = time.time()  # 结束时间

        # 打印查询花费时间
        print(f"查询花费时间：{end_query_time - start_query_time} 秒")

        # 打印或处理查询结果
        for row in cursor:
            print(row)
    finally:
        cursor.close()
        conn.close()

# 定义查询参数
station_id = 102000008
start_time = '2024-04-06 00:00:00'
end_time = '2024-04-07 00:00:00'

# 调用查询函数，传入参数
query_data(station_id, start_time, end_time)