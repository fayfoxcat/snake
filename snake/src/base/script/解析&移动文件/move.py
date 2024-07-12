#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import zipfile
import shutil
import sys
import codecs


def read_zip_files_in_directory(directory):
    file_name_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.zip'):
                zip_path = os.path.join(root, file)
                zip_ref = zipfile.ZipFile(str(zip_path), 'r')
                try:
                    file_name_list.extend(zip_ref.namelist())
                finally:
                    zip_ref.close()
    return file_name_list


def build_name_path_dict(directory):
    name_path_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            name_path_dict[file] = file_path
    return name_path_dict


def move_files(match_dict, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    for file_name, file_path in match_dict.items():
        dest_path = os.path.join(destination_dir, file_name)
        shutil.move(str(file_path), str(dest_path))


def save_list_to_file(data, file_path):
    f = codecs.open(file_path, 'w', encoding='utf-8')
    try:
        for item in data:
            f.write("%s\n" % item)
    finally:
        f.close()


def save_dict_to_file(data, file_path):
    f = codecs.open(file_path, 'w', encoding='utf-8')
    try:
        for key, value in data.items():
            f.write("%s: %s\n" % (key, value))
    finally:
        f.close()


def main(a_dir, s_dir, p_dir, t_dir):
    file_name_list = read_zip_files_in_directory(s_dir)
    name_path_dict = build_name_path_dict(a_dir)

    match_dict = {}
    for file_name in file_name_list:
        if file_name in name_path_dict:
            match_dict[file_name] = name_path_dict[file_name]

    if not os.path.exists(p_dir):
        os.makedirs(p_dir)
    move_files(match_dict, p_dir)

    if not os.path.exists(t_dir):
        os.makedirs(t_dir)
    print("sources file count: ", len(file_name_list))
    print("target file count: ", len(name_path_dict))
    print("match file count: ", len(match_dict))
    print("details for path: ", t_dir)
    save_list_to_file(file_name_list, os.path.join(t_dir, '源目录（S目录）文件名.txt'))
    save_dict_to_file(name_path_dict, os.path.join(t_dir, '目标目录(C目录)文件信息.txt'))
    save_dict_to_file(match_dict, os.path.join(t_dir, '匹配文件信息.txt'))


if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    a_dir = "/home/cne_illegal/audit"
    s_dir = "/home/sources"
    p_dir = os.path.join(script_dir, 'pending')
    t_dir = os.path.join(p_dir, 'logs')
    main(a_dir, s_dir, p_dir, t_dir)
