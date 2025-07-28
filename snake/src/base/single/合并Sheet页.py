import os
import pandas as pd
from openpyxl import load_workbook

def merge_sheets_to_single_excel(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(('.xlsx', '.xls')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # 读取原Excel的所有Sheet
            excel_data = pd.read_excel(input_path, sheet_name=None)  # 读取所有Sheet
            all_sheets = list(excel_data.values())  # 获取所有Sheet的数据

            # 合并所有Sheet（纵向追加）
            merged_data = pd.concat(all_sheets, ignore_index=True)

            # 写入新Excel（只有一个Sheet）
            merged_data.to_excel(output_path, index=False, sheet_name="Merged_Sheet")
            print(f"处理完成: {filename}")

if __name__ == "__main__":
    input_directory = 'C:/Users/root/Desktop/数据/'
    output_directory = os.path.join(input_directory, 'output')
    merge_sheets_to_single_excel(input_directory, output_directory)
    print("所有文件处理完成！")