from typing import List

import pandas as pd
#####################################################################################

# 文件路径
# file: str = 'C:/Users/fayfo/Desktop/工作簿+++.xlsx'
# 读取Excel文件,类型为字符串
# data = pd.read_excel(file, sheet_name='汇总', dtype='str')

#####################################################################################

# 文件路径
# file: str = 'C:/Users/fayfo/Desktop/数据.cvs'
# 读取cvs文件,类型为字符串
# data = pd.read_csv(file, sheet_name='汇总', dtype='str')

#####################################################################################
# 打印前五行
# print(data.head())

# 打印行数和列数
# print(data.shape)

# 打印数据列的数据类型
# print(data.dtypes)

#####################################################################################
# 设置数据
# myDataSet = {
#     'id': [1, 2, 3],
#     'name': ['姜泥', '徐凤年', '大官子曹长卿'],
#     'age': [18, 24, 32],
# }

# 格式化数据
# frameData = pd.DataFrame(myDataSet)

# print(frameData)

####################################################################################
# 声明list
# array: List[str] = ['第一行', '第二行', '第三行']

# 设置数据
# series = pd.Series(array)

# 打印数据
# print(series)

# 索引值就从 0 开始读取数据
# print(series[1])

# indexData = pd.Series(array, index=["x", "y", "z"])

# print(indexData)

# 以index读取数据
# print(indexData['x'])
####################################################################################
# 数据源
# db = [['张三', 10], ['李四', 12], ['王五', 13]]

# 数据载入到 DataFrame 对象,设置列名
# df = pd.DataFrame(db, columns=['name', 'age'], dtype=str)
'''
- excel_writer :目标路径
- sheet_name :填充excel的第几页
- na_rep :缺失值填充
- float_format : 输出格式
- columns : 选择输出的的列。
- header : 是否输出列名，默认True
- index : 是否输出index列，默认True
- index_label : 字符串或序列，默认无，如果需要，索引列的列标签。如果没有给出，并且header 和index 为True，则使用索引名称。如果 DataFrame 使用 MultiIndex，则应给出序列。
- merge_cells : 布尔值，默认 True 将 MultiIndex 和 Hierarchical Rows 写入合并单元格。
- encoding：字符串，结果excel文件的默认无编码。仅 xlwt 需要，其他作者本机支持 unicode。
'''
# 输出到文件
# df.to_excel('C:/Users/fayfo/Desktop/测试.xlsx')

###################################################################################
