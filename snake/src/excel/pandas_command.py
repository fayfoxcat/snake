import pandas as pd
import win32api
import win32con

# 文件路径
filePath: str = "C:/Users/cat/Desktop/HD公司主要会计数据和财务指标.xlsx"
# 读取excel工作簿Sheet1
excel_data = pd.read_excel(filePath, sheet_name="Sheet1", dtype='str')

# 表头和数据行
row_data = excel_data.iloc[9, [1, 2, 3]]
strout1 = list(excel_data.columns)
strout2 = list(row_data)

# 增长率
hyzzl: float = 0.19
zzl1 = float(strout2[0]) / float(strout2[1]) - 1
zzl2 = float(strout2[1]) / float(strout2[2]) - 1
strYear1 = strout1[1]
strYear2 = strout1[2]

# 逻辑判断
if zzl1 > hyzzl and zzl1 > zzl2:
    print(strYear1 + "净资产增长率考核结果：优秀！具体说明：HD公司" + strYear1 + "净资产增长率为" + '{:.2%}'.format(zzl1) +
          ",高于" + strYear1 + "同行业上市公司的平均净资产增长率" + '{:.2%}'.format(hyzzl) + ",并高于" + strYear1 +
          "公司的净资产增长率" + '{:.2%}'.format(zzl2) + ",反映了HD公司资产规模扩张速度较快，并且具有很好的发展潜力！")
elif hyzzl >= zzl1 > zzl2:
    print(strYear1 + "净资产增长率考核结果：良好！具体说明：HD公司" + strYear1 + "净资产增长率为" + '{:.2%}'.format(zzl1) +
          "，高于" + strYear1 + "同行业上市公司的平均净资产增长率" + '{:.2%}'.format(hyzzl) + "，但低于公司" + strYear2 +
          "公司的净资产增长率" + '{:.2%}'.format(zzl2) + "，反映了HD公司发展能力优于同行业上市公司平均水平，但其资产规模扩张速度减缓！")
elif hyzzl < zzl1 <= zzl2:
    print(strYear1 + "净资产增长率考核结果：达标！具体说明：HD公司" + strYear1 + "净资产增长率为" + '{:.2%}'.format(zzl1) +
          "，低于" + strYear1 + "同行业上市公司的平均净资产增长率" + '{:.2%}'.format(hyzzl) + "，但高于公司" + strYear2 +
          "公司的净资产增长率" + '{:.2%}'.format(zzl2) + "，反映了HD公司发展能力虽然低于同行业平均水平，但其资产规模扩张速度较快！")
else:
    print(strYear1 + "净资产增长率考核结果：不达标！具体说明：HD公司" + strYear1 + "净资产增长率为" + '{:.2%}'.format(zzl1) +
          "，低于" + strYear1 + "同行业上市公司的平均净资产增长率" + '{:.2%}'.format(hyzzl) + "，并且低于公司" + strYear2 +
          "公司的净资产增长率" + '{:.2%}'.format(zzl2) + "，反映了HD公司发展能力逊于同行业上市公司平均水平，并且资产规模扩张速度减缓！")

win32api.MessageBox(0, "", "结果", win32con.MB_OK)
