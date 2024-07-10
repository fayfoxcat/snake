import os
import webbrowser

import pandas as pd
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox


def parse_filename(filename):
    parts = filename.split('_')
    station = parts[0]
    date = parts[1]
    time = parts[2]
    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    return station, formatted_date, time


def extract_data_from_file(filepath):
    with open(filepath, 'r', encoding='ISO-8859-1') as file:
        lines = file.readlines()
    for line in lines:
        if line.strip().startswith('#1'):
            value = line.strip().replace('#1', '')
            return value
    return None


def process_files(folder_path):
    data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.WPD'):
            filepath = os.path.join(folder_path, filename)
            station, date, time = parse_filename(filename)
            value = extract_data_from_file(filepath)
            if station not in data:
                data[station] = {}
            if date not in data[station]:
                data[station][date] = {}
            data[station][date][time] = value
    return data


def create_excel(data, output_path):
    # 检查文件是否存在，如果存在，添加后缀
    base_name = "result"
    suffix = 0
    file_name = f"{base_name}.xlsx"
    while os.path.exists(os.path.join(output_path, file_name)):
        suffix += 1
        file_name = f"{base_name}_{suffix}.xlsx"
    full_path = os.path.join(output_path, file_name)

    writer = pd.ExcelWriter('output/result.xlsx', engine='openpyxl')
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
            max_length = 15
            worksheet.column_dimensions[col[0].column_letter].width = max_length

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
        output_path = os.path.abspath('output')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        excel_path = create_excel(data, output_path)
        label.config(text=excel_path)
        label.bind("<Button-1>", lambda e: webbrowser.open(excel_path))
        print(f"处理完成，结果已保存至：{excel_path}")
        messagebox.showinfo("完成", f"处理完成，结果已保存至：\n{excel_path}")
    else:
        print("未选择任何文件夹。")


def create_gui():
    root = Tk()
    root.title("文件处理程序")
    root.geometry('550x80')  # 设置窗口的宽度和高度

    entry = Entry(root, width=60)
    entry.grid(row=0, column=1, columnspan=2)

    Button(root, text="选择文件夹", command=lambda: select_folder(entry)).grid(row=0, column=0)
    Button(root, text="执行", command=lambda: run_process(entry, result_label)).grid(row=0, column=3, sticky='e')

    result_label = Label(root, text="", fg="blue", cursor="hand2")
    result_label.grid(row=1, column=0, columnspan=4)

    root.mainloop()

create_gui()
