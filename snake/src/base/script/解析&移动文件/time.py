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
        return file_time < (mod_time + timedelta(minutes=14))
    except Exception:
        print("Error getting modification time for file: ", file_path)
        print("Exception details:", sys.exc_info())
        return False


def main(folder_path):
    invalid_files = {}

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_time = get_file_info(file_name)

            if file_time and not check_file_modification_time(file_path, file_time):
                invalid_files[file_name] = file_path

    # 将结果写入非法文件.txt
    output_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'illegal.txt')
    f = codecs.open(output_file, 'w', encoding='utf-8')
    try:
        for file_name, file_path in invalid_files.items():
            f.write("%s: %s\n" % (file_name, file_path))
    finally:
        f.close()

    print("Results written to:", output_file)


if __name__ == "__main__":
    # 指定要检查的文件夹路径
    folder_path = '/home/cne_illegal/audit'
    main(folder_path)
