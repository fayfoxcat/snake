import subprocess

try:
    while True:
        dst = 'ping ' + input('请输入ip地址：')
        result = subprocess.run(dst, stdout=subprocess.PIPE)
        print(result.stdout)
        if str(result).__contains__('(0% '):
            print('能ping通该地址')
        else:
            print('ping不通该地址')
except Exception as r:
    print('未知错误 %s' % r)
