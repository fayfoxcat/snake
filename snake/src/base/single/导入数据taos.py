import pandas as pd
import taos


# 读取Excel文件
def read_excel(file_path):
    data = pd.read_excel(file_path, sheet_name='AGC点号')
    return data


# 连接TDengine数据库
def connect_taos():
    conn = taos.connect(host="172.18.37.208", user="root", password="taosdata", database="elss")
    cursor = conn.cursor()
    return cursor


# 创建子表
def create_subtable(cursor, data):
    for index, row in data.iterrows():
        station_id = row['电站ID']
        agc_id = row['AGC_ID']
        table_name = 'agc_telemetry_' + str(station_id) + '_' + str(agc_id)
        sql = "create table if not exists {} using agc_telemetry tags({}, {})".format(table_name, station_id, agc_id)
        cursor.execute(sql)


def main():
    file_path = 'C:/Users/root/Desktop/电站清单及AGC点号.xlsx'  # Excel文件路径
    data = read_excel(file_path)  # 读取Excel文件数据
    cursor = connect_taos()  # 连接TDengine数据库
    create_subtable(cursor, data)  # 创建子表


if __name__ == "__main__":
    main()
