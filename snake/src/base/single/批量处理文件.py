import concurrent.futures
import glob
import os
import re  # 导入正则表达式模块


def truncate_numeric(match):
    numeric = match.group(0)
    # 保留前38位，如果包含小数点或负号，这些也算在内
    truncated = numeric[:38]
    return truncated


# 全局变量，控制读取每个文件的最大长度，如果maxline为负数则不限制每个文件的读取长度
maxLine = -1


def process_file(filename):
    lines = []
    with open(filename, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            if 0 < maxLine <= i:
                break
            for pattern, replacement in replace_list:
                line = re.sub(pattern, replacement, line)  # 使用 re.sub 进行正则替换
            lines.append(line)

    result = ''.join(lines)
    if result is not None and result.strip() != '':
        new_filename = outputPath + os.path.basename(filename)
        with open(new_filename, 'w', encoding='utf-8') as file:
            file.write(result)


# 工作路径
rootPath = 'C:/Users/root/Desktop/SQL脚本处理/'
inputPath = rootPath + '/精简数据/*.sql'
outputPath = rootPath + '/结果数据/'

# 使用正则表达式进行匹配和替换
replace_list = [
    (r'public\.', ''),  # 移除 public. 前缀
    #(r'percent', 'percentage'),  # 替换 percent 为 percentage
    #(r'\border\b', 'sort'),  # 使用 \b 来匹配作为独立单词的 order/
    #(r'-?\d+(\.\d+)?', truncate_numeric),
    (r'"', '')  # 移除双引号
]

if not os.path.exists(outputPath):
    os.makedirs(outputPath)
with concurrent.futures.ThreadPoolExecutor() as executor:
    list(executor.map(process_file, glob.glob(inputPath)))
