import os
import shutil
import hashlib
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import psycopg2
from psycopg2.extras import RealDictCursor

pg_config = {
    'host': '172.18.31.230',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'dbname': 'ypm'
}
es_config = {
    'url': ['http://172.18.37.193:22030'],
    'basic_auth': ('elastic', 'wiscom123')
}


# StationInfo对象的定义
class StationInfo:
    def __init__(self, id, station_abbr, station_name):
        self.id = id
        self.station_abbr = station_abbr
        self.station_name = station_name


# FileRecord对象的定义
class FileRecord:
    def __init__(self, station_code, station_name, file_type, upload_time,
                 create_time, upload_status, plane_type, station_time_key):
        self.stationCode = station_code
        self.stationName = station_name
        self.fileType = file_type
        self.uploadTime = upload_time
        self.createTime = create_time
        self.uploadStatus = upload_status
        self.planeType = plane_type
        self.stationTimeKey = station_time_key


# 加密算法方法
def encrypt(plaintext):
    return hashlib.sha256(plaintext.encode()).hexdigest()


# 复制文件，复制加密文件
def copy_file(file_name, source_dir, clear_dir, cipher_dir):
    # 拷贝文件到cleartext目录
    src_path = str(os.path.join(source_dir, file_name))
    dst_path = str(os.path.join(clear_dir, file_name))
    shutil.copy2(src_path, dst_path)

    # 读取文件内容并加密
    with open(src_path, 'r') as file:
        content = file.read()
    encrypted_content = encrypt(content)

    # 写入密文到ciphertext目录
    cipher_dst_path = os.path.join(cipher_dir, file_name)
    with open(cipher_dst_path, 'w') as file:
        file.write(encrypted_content)
    shutil.copystat(src_path, cipher_dst_path)


# 向ES插入数据的方法
def insert_to_es(record, index):
    es = Elasticsearch(es_config.get('url'), basic_auth=es_config.get('basic_auth'))
    es.index(index=index, body=record)


# 向PG数据库查询数据的方法
def query_pg(sql):
    conn = psycopg2.connect(**pg_config)
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    conn.close()
    return result


# 获取StationInfo对象列表并转为字典
sql = "SELECT * FROM station_info"
station_info_list = query_pg(sql)
station_dict = {info['station_abbr']: StationInfo(info['id'], info['station_abbr'], info['station_name']) for info in
                station_info_list}

# 遍历target目录下的所有文件
target_dir = 'target'
cleartext_dir = 'cleartext'
ciphertext_dir = 'ciphertext'

if not os.path.exists(cleartext_dir):
    os.makedirs(cleartext_dir)
if not os.path.exists(ciphertext_dir):
    os.makedirs(ciphertext_dir)

for filename in os.listdir(target_dir):
    if filename.endswith('.WPD'):
        parts = filename.split('_')
        abbr = parts[0]
        date = parts[1]
        time = parts[2]
        suffix = parts[3].split('.')[0]
        # 复制文件到指定目录
        copy_file(filename, target_dir, cleartext_dir, ciphertext_dir)

        # 创建FileRecord对象
        station = station_dict.get(abbr)
        if station:
            if suffix == 'CDQ':
                upload_time = datetime.strptime(f"{date}_{time}", '%Y%m%d_%H%M') - timedelta(minutes=15)
            elif suffix == 'DQ':
                upload_time = datetime.strptime(date, '%Y%m%d') - timedelta(days=1, hours=-7, minutes=-30)
            else:
                upload_time = datetime.strptime(f"{date}_{time}", '%Y%m%d_%H%M')

            record = FileRecord(
                station_code=station.id,
                station_name=station.station_name,
                file_type=3,
                upload_time=upload_time,
                create_time=datetime.now(),
                upload_status=0,
                plane_type=1,
                station_time_key='abc.py'
            )
            # 插入ES数据库
            insert_to_es(record.__dict__, 'filerecord')
