import taosrest
import time

def connect_taos():
    try:
        print("尝试连接到TDengine数据库...")
        conn = taosrest.connect(url="http://172.18.37.208:6041", database="elss")
        print("连接成功")
        return conn
    except Exception as e:
        print(f"连接失败: {e}")
        raise

def query_data(station_id, start_time, end_time):
    conn = connect_taos()
    try:
        # Construct the query statement using parameters
        query = f"SELECT * FROM elss.agc_telemetry WHERE station_id = {station_id} AND collect_time >= '{start_time}' AND collect_time < '{end_time}' ORDER BY collect_time ASC;"
        print(f"执行查询: {query}")

        start_query_time = time.time()  # Start time
        result = conn.query(query)  # Execute the query
        end_query_time = time.time()  # End time

        # Print the time taken to execute the query
        print(f"查询花费时间：{end_query_time - start_query_time} 秒")

        # Print or process the query results
        for row in result:
            print(row)
    except taosrest.ExecutionError as e:
        print(f"查询失败: {e}")
    finally:
        conn.close()

# Define query parameters
station_id = 102000008
start_time = '2024-04-06 00:00:00'
end_time = '2024-04-07 00:00:00'

# Call the query function with parameters
query_data(station_id, start_time, end_time)
