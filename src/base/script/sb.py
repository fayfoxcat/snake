import requests

url = "http://112.124.67.183:8088/wiscom/mail/login"

# 定义表单数据
form_data = {
    'fingerprint_deviceid': 'd978bb5777d750f61b94f7147adccce3',
    'device_type': 'web',
    'device_name': 'edge',
    'sid': '',
    'uin': 'wiscom@wiscom.com.cn',
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

# 发送POST请求
while True:
    response = requests.post(url, data=form_data)
    # 打印响应内容
    print(response.status_code)
