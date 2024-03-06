line_count = 0
with open('C:/Users/root/Desktop/所有数据.sql', 'r', encoding='utf-8') as file:
    for line in file:
        line_count += 1

print(f'文件共有{line_count}行。')
