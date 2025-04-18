import json

import pandas as pd
from confluent_kafka import Producer

from src.base.script.kafka.KafkaAgcTelemetry import KafkaAgcTelemetry


def read_excel(file_path):
    # 使用pandas读取Excel文件
    return pd.read_excel(file_path, sheet_name=None, dtype={'STATION_ID': str})


def convert_row_to_object(row):
    # 将Excel行数据转换为KafkaAgcTelemetry对象
    return KafkaAgcTelemetry(
        devId=str(row['STATION_ID']),
        dataId=int(row['DATA_ID']),
        dataTime=int(row['DATA_TIME']),
        lower=convert_decimal(row['风场机组可调有功下限']),
        upper=convert_decimal(row['风场机组可调有功上限']),
        gen=convert_decimal(row['AGC控制对象有功功率']),
        pulse=convert_decimal(row['有功功率调节指令']),
        version=int(row['VERSION_ID'])
    )


def convert_decimal(value):
    # 检查是否为NaN，若是则返回None
    return None if pd.isna(value) else float(value)


def produce_to_kafka(topic, data_list):
    # 创建Producer实例
    producer = Producer({'bootstrap.servers': '172.18.37.248:9092'})

    # 批量发送数据
    for data in data_list:
        print("发送消息：{}", data)
        producer.produce(topic, json.dumps(data).encode('utf-8'))
    producer.flush()


def main():
    file_path = "C:/Users/root/Desktop/agc数据.xls"
    data = read_excel(file_path)

    for sheet_name, sheet_data in data.items():
        all_agc_telemetry_dicts = []  # 创建一个列表用于收集所有消息
        for _, row in sheet_data.iterrows():
            agc_telemetry = convert_row_to_object(row)
            # 转换对象为字典，用于JSON序列化
            agc_telemetry_dict = {
                '\"devID"': "\""+agc_telemetry.devId+"\"",
                '\"dataID"': agc_telemetry.dataId,
                '\"dataTime"': agc_telemetry.dataTime,
                '\"lower"': agc_telemetry.lower,
                '\"upper"': agc_telemetry.upper,
                '\"gen"': agc_telemetry.gen,
                '\"pulse"': agc_telemetry.pulse,
                '\"version"': agc_telemetry.version,
            }
            all_agc_telemetry_dicts.append(str(agc_telemetry_dict).replace("'","").replace("None", "null"))
        produce_to_kafka('a15d0fae09714a4db1b0e07c35659577_AgcDataToJZ', all_agc_telemetry_dicts)

    print("数据读取转换发送完成")


if __name__ == '__main__':
    main()
