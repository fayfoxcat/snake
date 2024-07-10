import requests as requests

# 基础url
baseUrl = 'http://192.168.60.100:5011/'
headers = {'Host': 'http://127.0.0.1:5000',
           'Connection': 'Keep-Alive',
           'Accept': 'application/json, text/plain, */*',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78',
           'X-Locale': 'zh',
           'X-SchoolId': 2,
           'X-Token': ""
           }

# 登录
url = baseUrl + "login/"
data = {'account': 'system@dipont.com', 'password': '123qwe.'}
r = requests.get(url, data)
print(r.json())

restPasswordUrl = baseUrl + 'student/resetParentPassword'

# 重置密码
get_url = 'http://127.0.0.1:5000/limit'
keyword = '{parentId:10}'

# result = requests.put(restPasswordUrl, params=keyword, timeout=2)
