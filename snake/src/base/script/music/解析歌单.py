import json


def parse_name(name):
    """ 分离歌手和歌曲名称 """
    # 通常歌手和歌曲之间有一个分隔符，这里假设是 ' - '
    parts = name.split(' - ')
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        return None, None  # 如果格式不正确，返回None


def process_json_file(input_filename, output_filename):
    """ 读取JSON文件，处理并写入新的JSON文件 """
    try:
        with open(input_filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        new_data = []

        for item in data:
            singer, song = parse_name(item.get('name', ''))
            if singer and song:
                new_data.append({'music': item.get('name', ''), 'singer': singer, 'song': song})

        with open(output_filename, 'w', encoding='utf-8') as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)

        print(f"新的 JSON 文件已保存为 {output_filename}")

    except Exception as e:
        print(f"处理文件时出错: {e}")


# 调用函数处理文件
process_json_file('form.json', 'new_form.json')
