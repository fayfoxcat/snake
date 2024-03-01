import os
import glob
import concurrent.futures

# 工作路径
rootPath = 'C:/Users/root/Desktop'
inputPath = rootPath + '/数据/*.sql'
outputPath = rootPath + '/数据2/'

# 要替换的字符串,关键词等
replace_list = [('"', ''), ('percent', 'percentage')]

# 全局变量，控制读取每个文件的最大长度，如果maxline为负数则不限制每个文件的读取长度
maxLine = 10000


def process_file(filename):
    lines = []
    with open(filename, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            if 0 < maxLine <= i:
                break
            for old_str, new_str in replace_list:
                line = line.replace(old_str, new_str)
            lines.append(line)

    result = ''.join(lines)
    if result is not None and result.strip() != '':
        new_filename = outputPath + os.path.basename(filename)
        with open(new_filename, 'w', encoding='utf-8') as file:
            file.write(result)


if not os.path.exists(outputPath):
    os.makedirs(outputPath)
with concurrent.futures.ThreadPoolExecutor() as executor:
    list(executor.map(process_file, glob.glob(inputPath)))
