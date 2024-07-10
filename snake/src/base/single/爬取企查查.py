import requests as requests

url = "https://www.qcc.com/api/datalist/partner"
# url = "https://www.qcc.com/firm/908af0142e5562698c3e5a32ed8e1487.html"
# url = "https://www.baidu.com"
# data = json.dumps({'account': 'system@dipont.com', 'password': '"123qwe.'})
# r = requests.get(url, data)
# print(r.status_code)

keyword = 'keyNo=908af0142e5562698c3e5a32ed8e1487&pageIndex=1&pageSize=50'
headers = {
    '05e29cea4ad3cb9fdc4c': 'b94ea32fcc0edad022d9bcd00f6d84a7cd111e79188a980d22a15252487f4bc80527358e2c54fdca99cc8018094bb4d312e4b132adfee97704613573c551c8b7',
    ':authority': 'www.qcc.com',
    ':method': 'GET',
    ':path': '/api/datalist/partner?keyNo=908af0142e5562698c3e5a32ed8e1487&pageIndex=1&pageSize=50',
    ':scheme': 'https',
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cookie': 'qcc_did=ecfb8840-777e-432b-80e4-1dd1b5fef9b6; QCCSESSID=45957e8c5cbd2b350d61f21d1d; zg_did=%7B%22did%22%3A%20%22183188e2ebff15-0c702e7023d0e8-72422e2e-384000-183188e2ec01052%22%7D; zg_d609f98c92d24be8b23d93a3e4b117bc=%7B%22sid%22%3A%201662564314819%2C%22updated%22%3A%201662564423169%2C%22info%22%3A%201662564314821%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22api.qichacha.com%22%7D; acw_tc=0884321116625649923936831e6362e7e4b75480a426563d007b55be8f',
    'referer': 'https://www.qcc.com/firm/908af0142e5562698c3e5a32ed8e1487.html',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Microsoft Edge";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70',
    'x-pid': '84fab6fd2e62fd7ac3c56966520788dc',
    'x-requested-with': 'XMLHttpRequest'
}
# for i in range(10):
# 休眠0.5s
# time.sleep(0.5)
result = requests.get(url, keyword, timeout=200)
print(result)
