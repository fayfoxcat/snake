import os
import re
import webbrowser
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, filedialog
import pandas as pd
from openpyxl.styles import Border, Side, Alignment
import threading


# 打包命令：pyinstaller --onefile --add-data "icon.ico;." --icon=.\icon.ico --windowed .\fileParse.py

def parse_filename(filename):
    station, date, time = filename.split('_')[:3]
    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    return station, formatted_date, time


def extract_data_from_file(filepath, line_num, value_pos):
    def try_convert_to_number(value):
        try:
            return float(value)  # 尝试转换为浮点数
        except ValueError:
            return value  # 如果转换失败，则保持原样返回

    pattern = re.compile(rf'^#{line_num}(?!\d)')  # 根据传入的数字定义一个正则表达式模式，匹配以#数字开头的行
    with open(filepath, 'r', encoding='ISO-8859-1') as file:
        skip_first:bool = True
        for line in file.readlines():
            match = pattern.match(line.strip())  # 尝试匹配每一行
            if match:
                if skip_first:
                    skip_first = False
                    continue
                if line.strip().__contains__('#'):
                    values = line.strip().split()[1:]  # 获取行中以空格分隔的所有值，忽略第一个元素（即#数字部分）
                    if len(values) >= value_pos:  # 检查是否有足够的值
                        return try_convert_to_number(values[value_pos - 1])  # 返回指定位置的值（索引从0开始，所以需要减1）
                    else:
                        return None  # 如果指定位置的值不存在，则返回None
    return None


def process_files(folder_path, percent_label, stop_event):
    data = {}
    file_count = sum([len(files) for _, _, files in os.walk(folder_path) if any(f.endswith('.WPD') for f in files)])
    current_count = 0

    for root, _, files in os.walk(folder_path):
        if stop_event.is_set():
            break
        for filename in files:
            if stop_event.is_set():
                break
            if filename.endswith('.WPD'):
                station, date, time = parse_filename(filename)
                formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y/%m/%d')
                value = extract_data_from_file(os.path.join(root, filename), 1, 1)
                data.setdefault(station, {}).setdefault(formatted_date, {})[f"{time[:2]}:{time[2:]}"] = value

                # 更新百分比标签
                current_count += 1
                percent_value = (current_count / file_count) * 100
                percent_label.config(text=f"{percent_value:.2f}%", font=("Helvetica", 12, "bold"))
                percent_label.update()

    return data


def create_excel(data, output_path):
    os.makedirs(output_path, exist_ok=True)
    file_name = "result.xlsx"
    full_path = os.path.join(output_path, file_name)

    writer = pd.ExcelWriter(full_path, engine='openpyxl')
    time_columns = [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in range(0, 60, 5)]

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

        worksheet = writer.sheets[station]
        for col in worksheet.columns:
            worksheet.column_dimensions[col[0].column_letter].width = 15

        border = Border(left=Side(style=None), right=Side(style=None), top=Side(style=None), bottom=Side(style=None))
        center_alignment = Alignment(horizontal='center', vertical='center')

        for row in worksheet.iter_rows():
            for cell in row:
                cell.border = border
                cell.alignment = center_alignment

    writer.close()
    return full_path


def select_folder(entry, stop_event, percent_label):
    stop_event.set()  # 终止当前处理程序
    folder_path = filedialog.askdirectory()
    entry.delete(0, 'end')
    entry.insert(0, folder_path)
    percent_label.config(text="")  # 重置百分比标签


def run_process(entry, label, percent_label, stop_event):
    stop_event.clear()  # 清除停止事件
    folder_path = entry.get()
    if folder_path:
        percent_label.grid(row=1, column=0, columnspan=4, padx=5, pady=10, sticky='n')  # 显示百分比标签

        # 使用线程来运行文件处理过程
        thread = threading.Thread(target=process_and_create_excel, args=(folder_path, label, percent_label, stop_event))
        thread.start()
    else:
        label.config(text="未选择任何文件夹！")
        print("未选择任何文件夹。")


def process_and_create_excel(folder_path, label, percent_label, stop_event):
    data = process_files(folder_path, percent_label, stop_event)
    if data:
        output_path = os.path.abspath('output')
        excel_path = create_excel(data, output_path)
        label.config(text=excel_path)
        label.bind("<Button-1>", lambda e: webbrowser.open(excel_path))
        print(f"处理完成，结果已保存至：{excel_path}")
    else:
        label.config(text="未找到符合条件的文件，请重新选择文件夹！")
        print("未找到符合条件的文件，请重新选择文件夹！")

    percent_label.grid_forget()  # 隐藏百分比标签


def center_window(root, width, height):
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = (screen_width - width) // 2, (screen_height - height) // 3
    root.geometry(f'{width}x{height}+{x}+{y}')


def create_gui():
    root = Tk()
    root.title("文件处理程序 Plus")
    root.resizable(False, False)
    center_window(root, 560, 160)

    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    root.iconbitmap(icon_path)
    root.configure(bg='white')

    entry = Entry(root, width=60)
    entry.grid(row=0, column=1, columnspan=2, padx=0, pady=(15, 0), ipady=3)

    percent_label = Label(root, text="", bg='white')

    result_label = Label(root, text="", fg="blue", bg='white', cursor="hand2", wraplength=500)
    result_label.grid(row=2, column=0, columnspan=4, padx=5, pady=10)

    stop_event = threading.Event()

    Button(root, text="选择文件夹", command=lambda: select_folder(entry, stop_event, percent_label), height=1).grid(
        row=0, column=0, padx=(16, 0),
        pady=(15, 0), sticky='w')
    Button(root, text="执行", command=lambda: run_process(entry, result_label, percent_label, stop_event),
           height=1).grid(
        row=0, column=3, padx=(0, 16), pady=(15, 0), sticky='e')

    root.mainloop()


create_gui()
