import os
import webbrowser
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, filedialog

import pandas as pd
from openpyxl.styles import Border, Side, Alignment


# 打包命令：pyinstaller --onefile --add-data "icon.ico;." --icon=.\icon.ico --windowed .\fileParse.py

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


def select_folder(entry):
    folder_path = filedialog.askdirectory()
    entry.delete(0, 'end')  # 清空entry
    entry.insert(0, folder_path)  # 插入新的文件夹路径


def run_process(entry, label):
    folder_path = entry.get()
    if folder_path:
        data = process_files(folder_path)
        if data:
            output_path = os.path.abspath('output')
            excel_path = create_excel(data, output_path)
            label.config(text=excel_path)
            label.bind("<Button-1>", lambda e: webbrowser.open(excel_path))
            print(f"处理完成，结果已保存至：{excel_path}")
        else:
            label.config(text="未找到符合条件的文件，请重新选择文件夹！")
            print("未找到符合条件的文件，请重新选择文件夹！")
    else:
        label.config(text="未选择任何文件夹！")
        print("未选择任何文件夹。")


def center_window(root, width, height):
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = (screen_width - width) // 2, (screen_height - height) // 3
    root.geometry(f'{width}x{height}+{x}+{y}')


def create_gui():
    root = Tk()
    root.title("文件处理程序")
    root.resizable(False, False)
    # 设置窗口的宽度和高度
    center_window(root, 560, 100)
    # 设置窗口图标
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    root.iconbitmap(icon_path)
    # 设置窗口背景颜色为白色
    root.configure(bg='white')

    entry = Entry(root, width=60)
    entry.grid(row=0, column=1, columnspan=2, padx=0, pady=(15, 0), ipady=3)

    (Button(root, text="选择文件夹", command=lambda: select_folder(entry), height=1)
     .grid(row=0, column=0, padx=(16, 0), pady=(15, 0), sticky='w'))
    (Button(root, text="执行", command=lambda: run_process(entry, result_label), height=1)
     .grid(row=0, column=3, padx=(0, 16), pady=(15, 0), sticky='e'))

    result_label = Label(root, text="", fg="blue", bg='white', cursor="hand2", wraplength=500)
    result_label.grid(row=1, column=0, columnspan=4, padx=5, pady=10)

    root.mainloop()


create_gui()
