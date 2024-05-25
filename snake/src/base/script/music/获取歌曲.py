import json
import requests
from bs4 import BeautifulSoup


# 读取JSON文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


# 获取搜索结果页面的URL
def get_search_page_url(music):
    base_url = "https://xiageba.com/s?keywords="
    return base_url + music.replace(" ", "+")


# 解析搜索结果页面，获取第一个有效的音乐链接
def parse_search_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    search_items = soup.find_all('div', class_='search-item row')
    if search_items:
        first_music_link = search_items[0].find('a', class_='link-blue')['href']
        return "https://xiageba.com" + first_music_link
    return None


# 获取下载链接页面
def get_download_link_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        download_div = soup.find('div', class_='down-item align-items-center')
        if download_div:
            span_text = download_div.find('span')
            if "夸克下载链接" in span_text.text:
                download_link = download_div.find('a')['href']
                return download_link
    return None


# 主流程
def main(json_file_path):
    music_data = read_json_file(json_file_path)
    for item in music_data:
        search_url = get_search_page_url(item['music'])
        search_page_response = requests.get(search_url)
        if search_page_response.status_code == 200:
            music_page_url = parse_search_results(search_page_response.text)
            if music_page_url:
                download_link = get_download_link_page(music_page_url)
                if download_link:
                    # 保存下载页面或进行进一步处理
                    print(f"Download link for {item['music']}: {download_link}")


if __name__ == "__main__":
    json_file_path = 'new_form.json'
    main(json_file_path)
