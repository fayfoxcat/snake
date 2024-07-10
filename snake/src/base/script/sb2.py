import requests

url = "https://112.124.67.183"


# 定义发送请求的函数
def send_request(url):
    while True:
        response = requests.get(url)
        print(response.text)


# # 使用ThreadPoolExecutor创建线程池
# with ThreadPoolExecutor(max_workers=1) as executor:
#     # 启动多个线程同时发送请求
#     for _ in range(1):  # 这里设置为5个线程，您可以根据需求调整
#         executor.submit(send_request, url)

send_request(url)
