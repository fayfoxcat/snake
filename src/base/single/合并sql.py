import glob
import threading
import os
from queue import Queue


# 处理单个SQL文件的函数
def process_file(file_path, result_queue):
    table_to_inserts = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().startswith("INSERT INTO"):
                parts = line.strip().split(" VALUES ")
                table_name = parts[0].split(" ")[2]  # 假设表名是第三个词
                values_part = parts[1].strip().rstrip(';')
                if table_name not in table_to_inserts:
                    table_to_inserts[table_name] = [parts[0], []]
                table_to_inserts[table_name][1].append(values_part)

    # 将处理结果放入队列中
    for table_name, (insert_prefix, values_list) in table_to_inserts.items():
        batch_insert_sql = f"{insert_prefix} VALUES {', '.join(values_list)};"
        result_queue.put(batch_insert_sql)


# 遍历文件夹并使用多线程处理每个文件
def process_folder(folder_path, result_path):
    result_queue = Queue()
    threads = []
    # 使用glob.glob()查找所有匹配的.sql文件
    for file_path in glob.glob(folder_path, recursive=True):
        thread = threading.Thread(target=process_file, args=(file_path, result_queue))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 将结果写入新的SQL文件
    with open(result_path, 'w', encoding='utf-8') as result_file:
        while not result_queue.empty():
            result_file.write(result_queue.get() + "\n")


# 示例使用
folder_path = "C:/Users/root/Desktop/数据2/*.sql"
output_path = "C:/Users/root/Desktop/合并后数据.sql"
process_folder(folder_path, output_path)
