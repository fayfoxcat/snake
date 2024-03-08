import os
import glob
import re

# 工作路径
rootPath = 'C:/Users/root/Desktop'
inputPath = rootPath + '/sources/*.sql'
outputPath = rootPath + '/result/'
# 要替换的字符串,关键词等
replace_list = [(r'"public"\.', ''),
                (r'COLLATE', ''),
                (r'varchar ', 'varchar(255)'),
                (r'"pg_catalog"\."default"', ''),
                (r'USING btree', ''),
                (r'"pg_catalog"\."int2_ops"', ''),
                (r'"pg_catalog"\."int4_ops"', ''),
                (r'"pg_catalog"\."int8_ops"', ''),
                (r'"pg_catalog"\."date_ops"', ''),
                (r'"pg_catalog"\."timestamp_ops"', ''),
                (r'timestamp\(\d+\)', 'datetime'),
                (r'numeric\(\d+,\d+\)', 'numeric(38,0)'),
                (r'percent', 'percentage'),
                (r'\bCACHE\s+1;', ';'),
                (r'\border\b', 'sort'),
                (r'"', '')]
# 删除包含下列字符串的行
delete_list = ['OWNER TO', 'SELECT', 'INCREMENT 1',
               'MINVALUE  1', 'MAXVALUE', 'START 1']

if not os.path.exists(outputPath):
    os.makedirs(outputPath)
for filename in glob.glob(inputPath):
    lines = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            # 如果这一行包含要删除的字符串，就跳过这一行
            if any(delete_str in line for delete_str in delete_list):
                continue
            # 如果这一行包含要替换的字符串，就替换这个字符串
            for old_str, new_str in replace_list:
                line = re.sub(old_str, new_str, line)
            lines.append(line)

    result = ''.join(lines)

    new_filename = outputPath + os.path.basename(filename)
    with open(new_filename, 'w', encoding='utf-8') as file:
        file.write(result)
