import os
import sys
import pandas as pd
from datetime import datetime
from openpyxl.styles import Border, Side, Alignment


def parse_filename(filename):
    station, date, time = filename.split('_')[:3]
    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    return station, formatted_date, time


def extract_data_from_file(filepath):
    with open(filepath, 'r', encoding='ISO-8859-1') as file:
        for line in reversed(file.readlines()):
            if line.strip().startswith('#1 '):
                return line.strip().split('#1 ')[1]
    return None


def process_files(folder_path):
    data = {}
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.WPD'):
                station, date, time = parse_filename(filename)
                formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y/%m/%d')
                value = extract_data_from_file(os.path.join(root, filename))
                data.setdefault(station, {}).setdefault(formatted_date, {})[time] = value
    return data


def create_excel(data, output_path):
    os.makedirs(output_path, exist_ok=True)
    file_name = "result.xlsx"
    full_path = os.path.join(output_path, file_name)

    writer = pd.ExcelWriter(full_path, engine='openpyxl')
    time_columns = [f"{hour:02d}{minute:02d}" for hour in range(24) for minute in range(0, 60, 15)]

    for station, dates in data.items():
        df = pd.DataFrame(columns=['日期'] + time_columns)
        rows = []
        for date, times in dates.items():
            row = {time: val for time, val in times.items()}
            row['日期'] = date
            rows.append(row)
        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
        df.sort_values(by='日期', inplace=True)
        df.to_excel(writer, sheet_name=station, index=False)

        # 获取工作表对象
        worksheet = writer.sheets[station]
        # 设置列宽，例如将所有列的宽度设置为15
        for col in worksheet.columns:
            worksheet.column_dimensions[col[0].column_letter].width = 15
        # 设置边框线
        border = Border(left=Side(style=None), right=Side(style=None), top=Side(style=None), bottom=Side(style=None))
        # 设置对齐方式
        center_alignment = Alignment(horizontal='center', vertical='center')

        for row in worksheet.iter_rows():
            for cell in row:
                cell.border = border
                cell.alignment = center_alignment

    writer.close()
    return full_path  # 返回生成的文件的完整路径


def main(folder_path):
    if folder_path:
        data = process_files(folder_path)
        output_path = os.path.abspath('output')
        excel_path = create_excel(data, output_path)
        print(f"处理完成，结果已保存至：{excel_path}")
    else:
        print("未选择任何文件夹。")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python script.py <文件夹路径>")
    else:
        folder_path = sys.argv[1]
        main(folder_path)
