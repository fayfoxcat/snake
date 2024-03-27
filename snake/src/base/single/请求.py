import http.client
import json

# 读取文件内容
with open('source.txt', 'r') as file:
    data = file.read()

args = json.dumps({
    'source': [data],
    'src_lang': 'eng_Latn',
    'tgt_lang': 'zho_Hans'
})
connect = http.client.HTTPConnection("localhost", 6060)
headers = {
    'Accept': '*/*',
    'Host': '127.0.0.1:6060',
    'Content-Type': 'application/json'
}

connect.request("POST", "/translate", args, headers=headers)
result = connect.getresponse().read()
print(result.decode("utf-8"))
