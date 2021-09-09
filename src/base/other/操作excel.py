import pandas as pd

# 文件路径
file: str = 'C:/Users/fayfo/Desktop/工作簿+++.xlsx'
# 读取文件,类型为字符串
data = pd.read_excel(file, sheet_name='汇总', dtype='str')

# 打印前五行
print(data.head())

# 打印行数和列数
# print(data.shape)

# 打印数据列的数据类型
# print(data.dtypes)
