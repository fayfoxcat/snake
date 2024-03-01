import subprocess
import time
import ctypes

# 蓝牙设备名
bluetooth_device_name = "喵~"

# 定义检查蓝牙连接状态的函数
def check_bluetooth_connection(device_name):
    # Windows系统使用命令行查询蓝牙设备列表
    result = subprocess.run(["powershell", "-Command", "Get-PnpDevice | Where-Object { $_.FriendlyName -like '*" + device_name + "*' } | Select-Object -ExpandProperty Status"], capture_output=True, text=True)
    status = result.stdout.strip()
    if "OK" in status:
        return True
    else:
        return False

# 定义锁定电脑的函数
def lock_computer():
    ctypes.windll.user32.LockWorkStation()

# 定义解锁电脑的函数
def unlock_computer():
    # Windows系统无法通过脚本直接解锁电脑，需要用户手动输入密码
    pass

# 主循环，定时检查蓝牙连接状态
previous_status = None
while True:
    connected = check_bluetooth_connection(bluetooth_device_name)
    if connected:
        if previous_status == False:
            print("蓝牙设备已连接，解锁电脑")
            unlock_computer()
        else:
            print("蓝牙设备已连接")
    else:
        if previous_status == True:
            print("蓝牙设备断开，锁定电脑")
            lock_computer()
        else:
            print("蓝牙设备未连接")

    previous_status = connected
    time.sleep(5)  # 每5秒检查一次
