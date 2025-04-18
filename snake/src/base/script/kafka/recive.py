import json
from confluent_kafka import Consumer, KafkaError

# Kafka 配置
bootstrap_servers = '28.47.67.6:9092'
group_id = 'PYTHON_KAFKA_TOPICS_AGC_TELEMETRY_2024_11_20'
topic = 'a15d0fae09714a4db1b0e07c35659577_AgcDataToJZ'

# 创建 Kafka 消费者
conf = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}

consumer = Consumer(conf)
consumer.subscribe([topic])

try:
    with open('agc_data.json', 'a', encoding='utf-8') as json_file:  # 以追加模式打开文件
        while True:
            msg = consumer.poll(1.0)  # 1秒超时
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # 到达分区末尾
                    continue
                else:
                    print("消费错误: {msg.error()}")
                    continue

            # 获取消息内容
            data = {
                'key': msg.key().decode('utf-8') if msg.key() else None,
                'value': msg.value().decode('utf-8') if msg.value() else None,
                'topic': msg.topic(),
                'partition': msg.partition(),
                'offset': msg.offset()
            }
            # 将消息写入 JSON 文件
            json.dump(data, json_file, ensure_ascii=False)
            json_file.write('\n')

except KeyboardInterrupt:
    print("消费停止。")
finally:
    consumer.close()