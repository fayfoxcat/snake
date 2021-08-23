import json

import requests as requests

url = "http://192.168.60.100:5011/login"
data = json.dumps({'account': 'system@dipont.com', 'password': '"123qwe.'})
r = requests.post(url, data)

print(r.text)
