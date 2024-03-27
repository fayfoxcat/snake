import socket
import threading

import errno
from tqdm import tqdm


# 判断输入的是域名还是IP地址
def is_valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False


# 支持IPv4
def is_port_open_ipv4(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)  # 超时时间（秒）
    try:
        sock.connect((ip, port))
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
            return "closed"
        else:
            return "filtered"
    else:
        sock.close()
        return "open"


# 支持IPv6
def is_port_open_ipv6(ip, port):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.settimeout(10)  # 超时时间（秒）
    try:
        sock.connect((ip, port, 0, 0))
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
            return "closed"
        else:
            return "filtered"
    else:
        sock.close()
        return "open"


# 格式化输出
def format_ports(ports):
    if not ports:
        return ""
    ports.sort()
    ranges = []
    start = ports[0]
    for i in range(1, len(ports)):
        if ports[i] != ports[i - 1] + 1:
            end = ports[i - 1]
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}~{end}")
            start = ports[i]
    if start == ports[-1]:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}~{ports[-1]}")
    return ', '.join(ranges)


# 扫描单个端口的函数
def scan_single_port(ip, port, ip_version, result):
    if ip_version:
        status = is_port_open_ipv4(ip, port)
    else:
        status = is_port_open_ipv6(ip, port)
    result[port] = status


def scan_ports(hostname, start=None, end=None):
    if start is not None and end is None:
        end = start + 1
    elif start is None and end is None:
        start = 0
        end = 20000
    try:
        # 判断输入的是域名还是IP地址
        if is_valid_ip(hostname):
            if ':' in hostname:
                ip_version = False
            else:
                ip_version = True
        else:
            # 获取地址信息，检查第一个返回的地址类型
            addr_info = socket.getaddrinfo(hostname, None)
            ip_type = addr_info[0][0]
            if ip_type == socket.AF_INET:
                ip_version = True
            elif ip_type == socket.AF_INET6:
                ip_version = False
            else:
                print("域名解释地址非法")
                return
    except socket.gaierror:
        print("地址非法或域名")
        return
    print(f"正在扫描 {hostname} 上的端口")
    result = {}
    with tqdm(total=end - start, desc="Progress") as pbar:
        for index, port in enumerate(range(start, end)):
            scan_single_port(hostname, port, ip_version, result)
            pbar.update(1)

    # 打印结果
    open_ports = [port for port, status in result.items() if status == "open"]
    closed_ports = [port for port, status in result.items() if status == "closed"]
    filtered_ports = [port for port, status in result.items() if status == "filtered"]

    print("活跃端口：" + format_ports(open_ports))
    print("关闭端口：" + format_ports(closed_ports))
    print("屏蔽端口：" + format_ports(filtered_ports))


# 输入域名或ip
scan_ports("dev.asac.cc", 443)
