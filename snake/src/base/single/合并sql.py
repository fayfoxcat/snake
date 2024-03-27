import glob
import mmap
import multiprocessing as mp


# 处理单个SQL文件的函数
def process_file(file_path, result_queue):
    table_to_inserts = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        for line in iter(mmapped_file.readline, b''):
            line = line.decode('utf-8')
            if line.strip().startswith("INSERT INTO"):
                parts = line.strip().split(" VALUES ")
                table_name = parts[0].split(" ")[2]  # 假设表名是第三个词
                values_part = parts[1].strip().rstrip(';')
                if table_name not in table_to_inserts:
                    table_to_inserts[table_name] = [parts[0], []]
                table_to_inserts[table_name][1].append(values_part)
                # 检查当前合并的VALUES数量是否已经达到20000条
                if len(table_to_inserts[table_name][1]) >= 5000:
                    batch_insert_sql = f"{table_to_inserts[table_name][0]} VALUES {', '.join(table_to_inserts[table_name][1])};"
                    result_queue.put(batch_insert_sql)
                    # 开始一条新的合并
                    table_to_inserts[table_name] = [parts[0], []]

    # 处理循环结束后剩余的部分
    for table_name, (insert_prefix, values_list) in table_to_inserts.items():
        if values_list:  # 只有当values_list非空时才需要写入
            batch_insert_sql = f"{insert_prefix} VALUES {', '.join(values_list)};"
            result_queue.put(batch_insert_sql)


# 遍历文件夹并使用多进程处理每个文件
def process_folder(folder_path, result_path):
    manager = mp.Manager()
    result_queue = manager.Queue()
    pool = mp.Pool(mp.cpu_count())

    # 使用glob.glob()查找所有匹配的.sql文件
    for file_path in glob.glob(folder_path, recursive=True):
        pool.apply_async(process_file, args=(file_path, result_queue))

    pool.close()
    pool.join()

    # 将结果写入新的SQL文件
    with open(result_path, 'w', encoding='utf-8') as result_file:
        while not result_queue.empty():
            result_file.write(result_queue.get() + "\n")


if __name__ == "__main__":
    import time

    start_time = time.time()
    # 示例使用
    folder_path = "C:/Users/root/Desktop/SQL脚本处理/原始数据/精简数据/*.sql"
    output_path = "C:/Users/root/Desktop/SQL脚本处理/结果数据/结果.sql"
    process_folder(folder_path, output_path)

    end_time = time.time()
    print("运行时间：", end_time - start_time)
