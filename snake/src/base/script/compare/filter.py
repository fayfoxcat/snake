import json

# 读取JSON文件
def read_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# 读取TXT文件，返回一个列表，每个元素是一行
def read_txt_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

# 将数据写入新的JSON文件
def write_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    # 加载源数据
    sources = read_json_file('source.json')
    # 加载待匹配的歌曲名
    unmatched_songs = read_txt_file('unmatched_songs.txt')

    # 准备匹配结果
    matched_results = []

    # 查找匹配项
    for song in unmatched_songs:
        for source in sources:
            if source['song'] == song:
                matched_results.append(source)
                break

    # 写入新的JSON文件
    write_json_file('new_sources.json', matched_results)

if __name__ == "__main__":
    main()
