import taosrest
import sys
import json
import logging


def batch_insert_station(conn, predict_type, station_id, data_list):
    # 构建表名
    table_name = f"predict_discharge_{predict_type}_{station_id}"

    # 构建USING部分
    tags = f"('{predict_type}', null, null, '{station_id}')"

    # 构建VALUES部分
    values = ", ".join(
        f"('{item.get('timePoint', 'NULL')}', {item.get('measuredElectricity', 'NULL')},"
        f" {item.get('predictElectricity', 'NULL')}, {item.get('discharge', 'NULL')})"
        for item in data_list
    )

    # 构建完整的SQL语句
    sql = f"""
    INSERT INTO {table_name}
    USING predict_discharge TAGS {tags}
    VALUES {values}
    """

    # 执行SQL语句
    try:
        conn.execute(sql)
        logging.info("Data inserted successfully")
    except Exception as e:
        logging.error(f"Error inserting data: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 4:
        logging.error("Usage: script.py <predictType> <stationId> <dataFilePath>")
        sys.exit(1)

    try:
        # 从命令行参数接收
        predict_type = sys.argv[1]
        station_id = sys.argv[2]
        data_file_path = sys.argv[3]

        # 从文件中读取数据
        with open(data_file_path, 'r') as f:
            data_list = json.load(f)

        # 数据库连接
        conn = taosrest.connect(url="http://172.18.31.4:6041", database="elss")

        # 调用插入函数
        batch_insert_station(conn, predict_type, station_id, data_list)
    except KeyError as e:
        logging.error(f"KeyError: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        # 关闭连接
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")
