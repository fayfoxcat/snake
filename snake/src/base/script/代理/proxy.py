import os
import sys
from ctypes import windll
from multiprocessing import freeze_support
from tkinter import Tk, Frame, Label, Button, Entry, scrolledtext

from PIL import Image
from pystray import Icon, MenuItem, Menu

import proxy_logic as logic


# 打包命令：pyinstaller --onefile --windowed --icon=proxy.ico --add-data "proxy.ico;." proxy.py

class ProxyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy")
        icon_path = os.path.join(os.path.dirname(__file__), 'proxy.ico')
        self.root.iconbitmap(icon_path)  # Set the window icon
        self.current_edit_index = None
        self.tray_icon = None  # Store the tray icon

        # Create log area
        self.create_log_area()

        # Load configurations
        logic.load_proxy_configs(self.log)

        # Create proxy list
        self.create_proxy_list()

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_proxy_list(self):
        """Create proxy list"""
        self.proxy_frame = Frame(self.root)
        self.proxy_frame.pack(pady=10)

        # Add header
        header_frame = Frame(self.proxy_frame)
        header_frame.pack(fill='x', pady=2)

        Label(header_frame, text="远程IP", width=20).pack(side='left', padx=5)
        Label(header_frame, text="远程端口", width=10).pack(side='left', padx=5)
        Label(header_frame, text="本地端口", width=10).pack(side='left', padx=5)
        Label(header_frame, text="操作", width=20).pack(side='left', padx=5)

        self.update_proxy_list()

    def update_proxy_list(self):
        """Update proxy list"""
        for widget in self.proxy_frame.winfo_children():
            if isinstance(widget, Frame) and widget != self.proxy_frame.winfo_children()[0]:
                widget.destroy()

        for idx, config in enumerate(logic.proxy_configs):
            self.add_proxy_row(idx, config)

        # Add new proxy input row
        self.add_proxy_input_row()

    def add_proxy_row(self, idx, config):
        """Add proxy row"""
        frame = Frame(self.proxy_frame)
        frame.pack(fill='x', pady=2)

        remote_host_label = Label(frame, text=config['remote_host'], width=19)
        remote_host_label.pack(side='left', padx=5)
        remote_port_label = Label(frame, text=config['remote_port'], width=10)
        remote_port_label.pack(side='left', padx=5)
        local_port_label = Label(frame, text=config['local_port'], width=10)
        local_port_label.pack(side='left', padx=5)

        button_text = "禁用" if config['enabled'] else "启用"
        toggle_button = Button(frame, text=button_text, command=lambda i=idx: self.toggle_proxy(i))
        toggle_button.pack(side='left', padx=5)

        edit_button = Button(frame, text="编辑", command=lambda i=idx: self.edit_proxy(i, frame))
        edit_button.pack(side='left', padx=5)

        Button(frame, text="删除", command=lambda i=idx: self.delete_proxy(i)).pack(side='left', padx=5)

    def edit_proxy(self, idx, frame):
        """Edit proxy"""
        if self.current_edit_index is not None and self.current_edit_index != idx:
            self.save_changes(self.current_edit_index)

        self.current_edit_index = idx
        config = logic.proxy_configs[idx]

        for widget in frame.winfo_children():
            widget.destroy()

        remote_host_entry = Entry(frame, width=20)
        remote_host_entry.insert(0, config['remote_host'])
        remote_host_entry.pack(side='left', padx=5)

        remote_port_entry = Entry(frame, width=10)
        remote_port_entry.insert(0, config['remote_port'])
        remote_port_entry.pack(side='left', padx=5)

        local_port_entry = Entry(frame, width=10)
        local_port_entry.insert(0, config['local_port'])
        local_port_entry.pack(side='left', padx=5)

        def save_changes():
            config['remote_host'] = remote_host_entry.get()
            config['remote_port'] = int(remote_port_entry.get())
            config['local_port'] = int(local_port_entry.get())
            self.current_edit_index = None

            if config['enabled']:
                logic.start_proxy(config, self.log)

            self.update_proxy_list()

        Button(frame, text="保存", command=save_changes).pack(side='left', padx=5)

    def add_proxy_input_row(self):
        """Add new proxy input row"""
        frame = Frame(self.proxy_frame)
        frame.pack(fill='x', pady=2)

        remote_host_entry = Entry(frame, width=20)
        remote_host_entry.pack(side='left', padx=5)

        remote_port_entry = Entry(frame, width=10)
        remote_port_entry.pack(side='left', padx=5)

        local_port_entry = Entry(frame, width=10)
        local_port_entry.pack(side='left', padx=5)

        def add_proxy():
            remote_host = remote_host_entry.get()
            remote_port = remote_port_entry.get()
            local_port = local_port_entry.get()

            if remote_host and remote_port.isdigit() and local_port.isdigit():
                new_config = {
                    'local_host': '127.0.0.1',
                    'local_port': int(local_port),
                    'remote_host': remote_host,
                    'remote_port': int(remote_port),
                    'enabled': False,
                    'server': None
                }
                logic.proxy_configs.append(new_config)
                self.update_proxy_list()
                self.log("新增代理配置")
            else:
                self.log("请填写完整的信息")

        Button(frame, text="保存", command=add_proxy).pack(side='left', padx=5)

    def create_log_area(self):
        """Create log area"""
        self.log_area = scrolledtext.ScrolledText(self.root, width=80, height=10)
        self.log_area.pack(pady=10)

    def log(self, message):
        """Log message"""
        self.log_area.insert('end', message + "\n")
        self.log_area.yview('end')

    def toggle_proxy(self, idx):
        """Toggle proxy"""
        config = logic.proxy_configs[idx]
        if config['enabled']:
            logic.stop_proxy(config, self.log)
            config['enabled'] = False
        else:
            logic.start_proxy(config, self.log)
            config['enabled'] = True

        self.update_proxy_list()

    def delete_proxy(self, idx):
        """Delete proxy"""
        config = logic.proxy_configs.pop(idx)
        logic.stop_proxy(config, self.log)
        self.log(f"删除代理: {config['local_host']}:{config['local_port']}")
        self.update_proxy_list()

    def minimize_to_tray(self):
        """Minimize to system tray"""
        self.root.withdraw()
        self.log("程序已最小化到系统托盘")
        if not self.tray_icon:
            self.create_tray_icon()

    def create_tray_icon(self):
        """Create system tray icon"""
        icon_path = os.path.join(os.path.dirname(__file__), 'proxy.ico')
        image = Image.open(icon_path)

        menu = Menu(
            MenuItem('显示主界面', self.show_main_window),
            MenuItem('退出', self.exit_app)
        )
        self.tray_icon = Icon("proxy_app", image, "代理工具", menu)
        self.tray_icon.run_detached()

    def show_main_window(self):
        """Show main window"""
        self.root.deiconify()
        self.root.after(0, self.root.lift)

    def exit_app(self):
        """Exit application"""
        try:
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.quit()
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            os._exit(0)

    def on_close(self):
        """Handle close event"""
        logic.save_proxy_configs(self.log)
        self.minimize_to_tray()


def is_already_running_mutex():
    # Create a mutex to ensure only one instance is running
    mutex_name = "my_unique_mutex_name"
    mutex = windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = windll.kernel32.GetLastError()

    if last_error == 183:  # ERROR_ALREADY_EXISTS
        return True
    return False


if __name__ == "__main__":
    freeze_support()  # For PyInstaller compatibility

    try:
        if is_already_running_mutex():
            print("程序已在运行中")
            sys.exit(0)

        root = Tk()
        app = ProxyApp(root)
        root.mainloop()
    except Exception as e:
        print(f"程序出错: {e}")
        input("按回车键退出...")
