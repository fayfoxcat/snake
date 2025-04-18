import json
import zipfile
from confluent_kafka import Producer

# 发送数据
def produce_to_kafka(topic, data_list):
    # 创建Producer实例
    producer = Producer({'bootstrap.servers': '172.18.37.248:9092'})

    # 批量发送数据
    for data in data_list:
        dev_id = data.get('"devID"').strip('"')
        timestamp = (data.get('"dataTime"') - 28800) * 1000
        key = f"{dev_id}:{timestamp}"
        producer.produce(
            topic,
            json.dumps(str(data).replace("'", "").replace("None", "null")).encode('utf-8'),
            key=key,
            timestamp=timestamp
        )
    producer.flush()


# 解析 JSON
def extract_fields(json_string):
    try:
        # json_string 应该是形如 {'value': '{...}'} 的字典
        inner_data = json.loads(json_string['value'])
        return json.loads(inner_data)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
    except KeyError as e:
        print(f"Missing key: {e}")
        return None


# 从指定的 zip 文件里读取所有 .json 文件，逐行返回 JSON 数据
def read_json_in_zip(zip_file_path):
    # 打开 zip 文件
    with zipfile.ZipFile(zip_file_path, 'r') as zf:
        # 获取 zip 文件内所有文件名，逐个检查是否以 .json 结尾
        for file_name in zf.namelist():
            if file_name.endswith('.json'):
                print(f"正在读取：{file_name}")
                # 以二进制方式打开，再手动 decode
                with zf.open(file_name, 'r') as file:
                    for line in file:
                        # 每行是一个 JSON 字符串，需要解码为 utf-8
                        yield json.loads(line.decode('utf-8'))


def main():
    # 目标 .zip 文件路径（示例）
    zip_file_path = 'C:/Users/root/Downloads/agc_data1231.zip'

    all_agc_telemetry_dicts = []
    index = 0
    batch_size = 10000

    # 逐行从 .zip 内的所有 .json 文件读取数据
    for data in read_json_in_zip(zip_file_path):
        agc_telemetry = extract_fields(data)
        if not agc_telemetry:
            continue

        # 转换对象为字典，用于 JSON 序列化
        agc_telemetry_dict = {
            '\"devID"': "\"" + agc_telemetry.get('devID') + "\"",
            '\"dataID"': agc_telemetry.get('dataID'),
            '\"dataTime"': agc_telemetry.get('dataTime'),
            '\"lower"': agc_telemetry.get('lower'),
            '\"upper"': agc_telemetry.get('upper'),
            '\"gen"': agc_telemetry.get('gen'),
            '\"pulse"': agc_telemetry.get('pulse'),
            '\"version"': agc_telemetry.get('version'),
        }
        all_agc_telemetry_dicts.append(agc_telemetry_dict)

        # 当列表长度达到指定大小时，发送数据到 Kafka
        if len(all_agc_telemetry_dicts) >= batch_size:
            index += 1
            produce_to_kafka('a15d0fae09714a4db1b0e07c35659577_AgcDataToJZ', all_agc_telemetry_dicts)
            print(f"已累计发送 {batch_size * index} 条数据，当前为第 {index} 批")
            all_agc_telemetry_dicts.clear()

    # 发送剩余的数据
    if all_agc_telemetry_dicts:
        produce_to_kafka('a15d0fae09714a4db1b0e07c35659577_AgcDataToJZ---', all_agc_telemetry_dicts)
        print(f"已累计发送 {len(all_agc_telemetry_dicts) + batch_size * index} 条数据，当前为第 {index + 1} 批")
    print("数据读取转换发送完成")


if __name__ == '__main__':
    main()