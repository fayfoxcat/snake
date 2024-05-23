import pandas as pd
import psycopg2

# PostgreSQL数据库连接参数
user = 'postgres'
password = 'postgres'
host = '172.18.37.208'
port = '5432'
database = 'elss'


def type_switch(case_str):
    switcher = {
        "海上风电": 1,
        "沿海风电": 2,
        "内陆风电": 3,
        "统调光伏": 4,
    }
    return switcher.get(case_str, None)


def district_switch(case_str):
    switcher = {
        "南京市": 5,
        "无锡市": 6,
        "徐州市": 7,
        "常州市": 8,
        "苏州市": 9,
        "南通市": 10,
        "连云港市": 11,
        "淮安市": 12,
        "盐城市": 13,
        "扬州市": 14,
        "镇江市": 15,
        "泰州市": 16,
        "宿迁市": 17,
    }
    return switcher.get(case_str, None)


# 连接到数据库
conn = psycopg2.connect(
    dbname=database,
    user=user,
    password=password,
    host=host,
    port=port
)

# 读取Excel文件
excel_path = "C:/Users/root/Desktop/场站信息.xls"
sheet_name = 'Sheet2'
df = pd.read_excel(excel_path, sheet_name=sheet_name, na_filter=False)

# 创建一个游标对象
cur = conn.cursor()
# 从第二行开始读取数据
df = df.where(pd.notnull(df), None)
print(df.columns)
# 遍历DataFrame的行
for index, row in df.iterrows():
    # 处理station_id为空的情况
    station_id = row['电站ID'] if row['电站ID'] != '' else None
    capacity = row['装机容量（MW）'] if row['装机容量（MW）'] != '' else None

    # 创建参数化插入语句
    insert_query = """
    INSERT INTO power_station (station_id, name, abbr, station_type, district_id, planning_capacity, capacity, margin, 
    switch_agc, clique, longitude, latitude, remark, creator, updater, create_time, update_time, delete_flag) 
    VALUES (%s, %s, %s, %s, %s, NULL, %s, 0.02, 't', '', 
    NULL, NULL, NULL, 1, NULL, '2024-05-01 00:00:00', NULL, 'f');
    """

    # 执行插入语句
    cur.execute(insert_query, (
        station_id,
        row['电站名称'],
        row['电站缩写'],
        type_switch(row['场站类型']),
        district_switch(row['城市']),
        capacity
    ))

# 提交事务
conn.commit()

# 关闭游标和连接
cur.close()
conn.close()
