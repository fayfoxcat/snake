import os
import webbrowser
from tkinter import Tk, Label, Button, Entry, filedialog

from parseFile import process_files, create_excel


# 打包命令：pyinstaller --onefile --add-data "icon.ico;." --icon=.\icon.ico --windowed .\fileParse.py

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
