import os
import tkinter as tk
from tkinter import scrolledtext
import pystray
from PIL import Image
import proxy_logic as logic

class ProxyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy")
        self.current_edit_index = None

        # 创建日志区域
        self.create_log_area()

        # 加载配置
        logic.load_proxy_configs(self.log)

        # 创建代理列表
        self.create_proxy_list()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_proxy_list(self):
        """创建代理列表"""
        self.proxy_frame = tk.Frame(self.root)
        self.proxy_frame.pack(pady=10)

        # 添加表头
        header_frame = tk.Frame(self.proxy_frame)
        header_frame.pack(fill=tk.X, pady=2)

        tk.Label(header_frame, text="远程IP", width=20).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="远程端口", width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="本地端口", width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="操作", width=20).pack(side=tk.LEFT, padx=5)

        self.update_proxy_list()

    def update_proxy_list(self):
        """更新代理列表"""
        for widget in self.proxy_frame.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.proxy_frame.winfo_children()[0]:
                widget.destroy()

        for idx, config in enumerate(logic.proxy_configs):
            self.add_proxy_row(idx, config)

        # 添加新的代理输入行
        self.add_proxy_input_row()

    def add_proxy_row(self, idx, config):
        """添加代理行"""
        frame = tk.Frame(self.proxy_frame)
        frame.pack(fill=tk.X, pady=2)

        remote_host_label = tk.Label(frame, text=config['remote_host'], width=19)
        remote_host_label.pack(side=tk.LEFT, padx=5)
        remote_port_label = tk.Label(frame, text=config['remote_port'], width=10)
        remote_port_label.pack(side=tk.LEFT, padx=5)
        local_port_label = tk.Label(frame, text=config['local_port'], width=10)
        local_port_label.pack(side=tk.LEFT, padx=5)

        button_text = "禁用" if config['enabled'] else "启用"
        toggle_button = tk.Button(frame, text=button_text, command=lambda i=idx: self.toggle_proxy(i))
        toggle_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(frame, text="编辑", command=lambda i=idx: self.edit_proxy(i, frame))
        edit_button.pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="删除", command=lambda i=idx: self.delete_proxy(i)).pack(side=tk.LEFT, padx=5)

    def edit_proxy(self, idx, frame):
        """编辑代理"""
        if self.current_edit_index is not None and self.current_edit_index != idx:
            self.save_changes(self.current_edit_index)

        self.current_edit_index = idx
        config = logic.proxy_configs[idx]

        for widget in frame.winfo_children():
            widget.destroy()

        remote_host_entry = tk.Entry(frame, width=20)
        remote_host_entry.insert(0, config['remote_host'])
        remote_host_entry.pack(side=tk.LEFT, padx=5)

        remote_port_entry = tk.Entry(frame, width=10)
        remote_port_entry.insert(0, config['remote_port'])
        remote_port_entry.pack(side=tk.LEFT, padx=5)

        local_port_entry = tk.Entry(frame, width=10)
        local_port_entry.insert(0, config['local_port'])
        local_port_entry.pack(side=tk.LEFT, padx=5)

        def save_changes():
            config['remote_host'] = remote_host_entry.get()
            config['remote_port'] = int(remote_port_entry.get())
            config['local_port'] = int(local_port_entry.get())
            self.current_edit_index = None

            if config['enabled']:
                logic.start_proxy(config, self.log)

            self.update_proxy_list()

        tk.Button(frame, text="保存", command=save_changes).pack(side=tk.LEFT, padx=5)

    def add_proxy_input_row(self):
        """添加新的代理输入行"""
        frame = tk.Frame(self.proxy_frame)
        frame.pack(fill=tk.X, pady=2)

        remote_host_entry = tk.Entry(frame, width=20)
        remote_host_entry.pack(side=tk.LEFT, padx=5)

        remote_port_entry = tk.Entry(frame, width=10)
        remote_port_entry.pack(side=tk.LEFT, padx=5)

        local_port_entry = tk.Entry(frame, width=10)
        local_port_entry.pack(side=tk.LEFT, padx=5)

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

        tk.Button(frame, text="保存", command=add_proxy).pack(side=tk.LEFT, padx=5)

    def create_log_area(self):
        """创建日志区域"""
        self.log_area = scrolledtext.ScrolledText(self.root, width=80, height=10)
        self.log_area.pack(pady=10)

    def log(self, message):
        """记录日志"""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)

    def toggle_proxy(self, idx):
        """启用或禁用代理"""
        config = logic.proxy_configs[idx]
        if config['enabled']:
            logic.stop_proxy(config, self.log)
            config['enabled'] = False
        else:
            logic.start_proxy(config, self.log)
            config['enabled'] = True

        self.update_proxy_list()

    def delete_proxy(self, idx):
        """删除代理"""
        config = logic.proxy_configs.pop(idx)
        logic.stop_proxy(config, self.log)
        self.log(f"删除代理: {config['local_host']}:{config['local_port']}")
        self.update_proxy_list()

    def minimize_to_tray(self):
        """最小化到系统托盘"""
        self.root.withdraw()
        self.log("程序已最小化到系统托盘")
        self.create_tray_icon()

    def create_tray_icon(self):
        """创建系统托盘图标"""
        icon_path = os.path.join(os.path.dirname(__file__), 'PROXY.ico')
        image = Image.open(icon_path)

        menu = pystray.Menu(
            pystray.MenuItem('显示主界面', self.show_main_window),
            pystray.MenuItem('退出', self.exit_app)
        )
        icon = pystray.Icon("proxy_app", image, "代理工具", menu)
        icon.run_detached()

    def show_main_window(self, icon, item):
        """显示主界面"""
        self.root.deiconify()
        self.root.after(0, self.root.lift)

    def exit_app(self, icon, item):
        """退出应用"""
        icon.stop()
        self.root.quit()

    def on_close(self):
        """关闭事件处理"""
        logic.save_proxy_configs(self.log)
        self.minimize_to_tray()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyApp(root)
    root.mainloop()
