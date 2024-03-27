import os
import tkinter as tk
from tkinter import ttk
import pywinusb as hid
from pywinusb.hid import find_all_hid_devices


def detect_device(device):
    print('检测到设备：{0}'.format(device))


def enable_device(device):
    os.system('devcon enable {0}'.format(device.hardware_id))  # 使用devcon工具启用设备


def disable_device(device):
    os.system('devcon disable {0}'.format(device.hardware_id))  # 使用devcon工具禁用设备


def restart_device(device):
    disable_device(device)
    enable_device(device)


def create_gui(devices):
    root = tk.Tk()
    tree = ttk.Treeview(root)
    tree["columns"] = ("one", "two", "three")
    tree.column("one", width=100)
    tree.column("two", width=100)
    tree.column("three", width=100)
    tree.heading("one", text="设备名称")
    tree.heading("two", text="启用")
    tree.heading("three", text="禁用")

    for device in devices:
        tree.insert("", 0, text=device, values=("启用", "禁用", "重启"))

    tree.pack()
    root.mainloop()


all_devices = find_all_hid_devices()
create_gui(all_devices)
