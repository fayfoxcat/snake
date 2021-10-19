import os

iplist = list()
ip = 'site.tea123.me'
result = os.system('ping '+ ip)  # 实现pingIP地址的功能，-c1指发送报文一次，-w1指等待1秒


if result:
    print('no')
else:
    iplist.append(ip)

print(iplist)

