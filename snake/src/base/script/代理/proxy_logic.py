import socket
import threading
import json
import os

# 保存代理配置的列表
proxy_configs = []

def load_proxy_configs(log_func):
    """加载代理配置"""
    try:
        user_dir = os.path.expanduser('~')
        file_path = os.path.join(user_dir, 'proxy.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_configs = json.load(f)
                for config in loaded_configs:
                    config['server'] = None  # 初始化时将服务器设置为None
                    proxy_configs.append(config)
            log_func("代理配置已加载")
    except Exception as e:
        log_func(f"加载代理配置时出错: {e}")

def save_proxy_configs(log_func):
    """保存代理配置"""
    try:
        user_dir = os.path.expanduser('~')
        file_path = os.path.join(user_dir, 'proxy.json')
        # 移除不可序列化的对象
        configs_to_save = [{k: v for k, v in config.items() if k != 'server'} for config in proxy_configs]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(configs_to_save, f, ensure_ascii=False, indent=4)
        log_func(f"代理配置已保存到 {file_path}")
    except Exception as e:
        log_func(f"保存代理配置时出错: {e}")

def start_proxy(config, log_func):
    """启动代理"""
    if not config['enabled']:
        config['enabled'] = True
        thread = threading.Thread(target=run_proxy, args=(config, log_func))
        thread.start()

def stop_proxy(config, log_func):
    """停止代理"""
    if config['enabled'] and config['server']:
        config['enabled'] = False
        try:
            config['server'].close()
            log_func(f"代理已关闭：{config['local_host']}:{config['local_port']}")
        except Exception as e:
            log_func(f"关闭代理时出错: {e}")

def run_proxy(config, log_func):
    """运行代理服务器"""
    local_host = config['local_host']
    local_port = config['local_port']
    remote_host = config['remote_host']
    remote_port = config['remote_port']

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((local_host, local_port))
        server.listen(5)
        config['server'] = server
        log_func(f"代理已启动：{local_host}:{local_port} -> {remote_host}:{remote_port}")

        while config['enabled']:
            client_socket, addr = server.accept()
            log_func(f"接受连接来自：{addr}")
            proxy_thread = threading.Thread(target=handle_client, args=(client_socket, remote_host, remote_port, log_func))
            proxy_thread.start()
    except Exception as e:
        print(f"错误: {e}")
    finally:
        if server:
            server.close()

def handle_client(client_socket, remote_host, remote_port, log_func):
    """处理客户端连接"""
    try:
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

        def forward_data(source, destination):
            while True:
                data = source.recv(4096)
                if len(data) == 0:
                    break
                destination.sendall(data)

        client_thread = threading.Thread(target=forward_data, args=(client_socket, remote_socket))
        remote_thread = threading.Thread(target=forward_data, args=(remote_socket, client_socket))

        client_thread.start()
        remote_thread.start()

        client_thread.join()
        remote_thread.join()
    finally:
        client_socket.close()
        remote_socket.close()
