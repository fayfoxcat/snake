from typing import List
import pymysql as db
import pandas as pd

# 连接数据库
conn = db.connect(host='localhost', port=3306, user='root', password='123456', database='api', charset='utf8')
cursor = conn.cursor()

# 查询数据
cursor.execute('SELECT * FROM `t_area`')
# 构建list
array: List[str] = [line for line in cursor.fetchall()]

# 数据载入到 DataFrame 对象
df = pd.DataFrame(array, columns=['序号', '省编码', '省份', '市编码', '城市', '县编码', '县'], dtype=str)

# 文件路径
file: str = 'C:/Users/fayfo/Desktop/数据.xlsx'

df.to_excel(excel_writer=file, sheet_name='数据', na_rep='', index=False)

# 关闭游标及连接
cursor.close()
conn.close()
