import os
import requests
from urllib.parse import quote

# 读取文件夹中的文件名
music_dir = r"C:\Users\root\Desktop\Music无封面"
files = os.listdir(music_dir)

# 定义保存路径
lyrics_dir = r"resources\lrc"
cover_dir = r"resources\cover"

# 确保保存目录存在
os.makedirs(lyrics_dir, exist_ok=True)
os.makedirs(cover_dir, exist_ok=True)

# 定义请求的 URL 和请求头
url = "https://www.jbsou.cn/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "X-Requested-With": "XMLHttpRequest"
}

# 遍历文件名，发送请求
for file_name in files:
    # 从文件名构建查询
    query = os.path.splitext(file_name)[0]  # 假设文件名即查询所需的歌曲名
    data = {
        "input": query,
        "filter": "name",
        "type": "netease",
        "page": 1
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        result = response.json()
        if result['data']:
            first_song = result['data'][0]
            # 保存歌词
            lyrics_path = os.path.join(lyrics_dir, f"{query}.lrc")
            with open(lyrics_path, 'w', encoding='utf-8') as f:
                f.write(first_song['lrc'])

            # 保存封面图片
            cover_url = first_song['pic'].split('?')[0]  # 移除可能的参数
            cover_response = requests.get(cover_url)
            if cover_response.status_code == 200:
                cover_path = os.path.join(cover_dir, f"{query}.jpg")
                with open(cover_path, 'wb') as f:
                    f.write(cover_response.content)

print("处理完成。")
