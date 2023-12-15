# 导入相关库
import requests
from bs4 import BeautifulSoup

# 请求豆瓣电影榜单页面
url = 'https://movie.douban.com/chart'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 创建一个空列表，用于存储电影数据
movie_data_list = []

# 抓取电影数据
movies = soup.find_all('div', class_='pl2')
for movie in movies:
    # 提取电影信息
    name = movie.a.text.strip()
    cover = movie.a.img['src']
    info = movie.p.text.strip().split('/')
    release_date = info.pop()
    rating = float(movie.parent.find('span', class_='rating_num').text)
    voters = int(movie.parent.find('span', class_='pl').text.strip('()人评价'))

    # 将电影信息以字典形式添加到列表中
    movie_data = {
        'movieName': name,
        'movieCover': cover,
        'movieRating': rating,
        'movieVoters': voters
    }
    movie_data_list.append(movie_data)

# 打印抓取的电影数据列表
print(movie_data_list)
