import os
import json

def read_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def find_flac_files(directory):
    flac_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".flac"):
                flac_files.append(file)
    return flac_files

def main():
    songs_data = read_json_file('source.json')
    song_list = [song['song'] for song in songs_data]
    flac_files = find_flac_files(r'C:\Users\root\Desktop\Music')

    matched_flac_count = 0
    matched_song_count = 0
    unmatched_flac_files = []
    unmatched_songs = list(song_list)

    for flac_file in flac_files:
        match_found = False
        for song in song_list:
            if song in flac_file:
                matched_flac_count += 1
                match_found = True
                if song in unmatched_songs:
                    unmatched_songs.remove(song)
                    matched_song_count += 1
                break
        if not match_found:
            unmatched_flac_files.append(flac_file)

    print("总.flac文件数量:", len(flac_files))
    print("匹配上的.flac数量:", matched_flac_count)
    print("未匹配上的.flac数量:", len(unmatched_flac_files))
    print("source中song总数量:", len(song_list))
    print("匹配上的song总数量:", matched_song_count)
    print("未匹配上song的总数量:", len(unmatched_songs))

    # 写入未匹配上的.flac文件列表和song列表到文件
    with open('unmatched_flac_files.txt', 'w', encoding='utf-8') as f:
        for flac_file in unmatched_flac_files:
            f.write(f"{flac_file}\n")
    with open('unmatched_songs.txt', 'w', encoding='utf-8') as f:
        for song in unmatched_songs:
            f.write(f"{song}\n")

    print("未匹配上的.flac文件列表已保存到 'unmatched_flac_files.txt'")
    print("未匹配上的song列表已保存到 'unmatched_songs.txt'")

if __name__ == '__main__':
    main()
