# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys
from datetime import datetime, timedelta


def get_file_info(file_name):
    try:
        # 定义正则表达式来匹配文件名中的时间部分
        pattern = r'(\d{8})_(\d{4})'
        match = re.search(pattern, file_name)

        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            # 手动解析日期和时间字符串
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            hour = int(time_str[0:2])
            minute = int(time_str[2:4])
            file_time = datetime(year, month, day, hour, minute)
            return file_time
        else:
            print("No matching date and time found in file name:", file_name)
            return None
    except Exception:
        print("Error parsing time from file name:", file_name)
        print("Exception details:", sys.exc_info())
        return None


def check_file_modification_time(file_path, file_time):
    try:
        # 获取文件的修改时间
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        # 判断文件的修改时间减去14分钟是否在指定时间之前
        return (mod_time + timedelta(minutes=14)) < file_time
    except Exception:
        print("Error getting modification time for file: ", file_path)
        print("Exception details:", sys.exc_info())
        return False


def main(folder_path):
    # 创建一个字典，用于存储非法的文件及其路径
    invalid_files = {}

    # 遍历文件夹及其子文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # 获取文件的完整路径
            file_path = os.path.join(root, file_name)
            # 获取文件名中的时间信息
            file_time = get_file_info(file_name)

            # 如果获取到的时间信息有效且文件的修改时间不符合要求
            if file_time and not check_file_modification_time(file_path, file_time):
                # 将非法文件的名称和路径添加到字典中
                invalid_files[file_name] = file_path

    # 结果将写入到非法文件.txt中
    output_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'illegal.txt')
    # 以写入模式打开文件，并指定编码为utf-8
    f = codecs.open(output_file, 'w', encoding='utf-8')
    try:
        # 将非法文件的信息写入到文件中
        for file_name, file_path in invalid_files.items():
            f.write("%s: %s\n" % (file_name, file_path))
    finally:
        # 关闭文件
        f.close()

    # 输出结果文件的路径
    print("Results written to:", output_file)


if __name__ == "__main__":
    # 指定要检查的文件夹路径
    folder_path = 'C:/Users/root/Documents/Project/cat/script/snake/src/base/script/解析&移动文件/test'
    main(folder_path)
