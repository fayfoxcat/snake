import os

from mutagen.flac import FLAC
from mutagen.id3 import ID3, USLT, error
from mutagen.mp3 import MP3


def embed_lyrics_from_lrc_to_flac(flac_file, lrc_file):
    # 读取 FLAC 文件
    audio = FLAC(flac_file)

    # 检查是否已经嵌入了歌词
    if "LYRICS" in audio:
        print(f"{flac_file} 已经包含歌词，不需要处理。")
        return

    # 尝试读取 LRC 文件中的歌词
    lyrics = read_lyrics(lrc_file)

    # 嵌入歌词到 FLAC 文件
    audio["LYRICS"] = lyrics
    audio.save()
    print(f"已将歌词嵌入到 {flac_file} 中。")


def embed_lyrics_from_lrc_to_mp3(mp3_file, lrc_file):
    # 读取 MP3 文件
    audio = MP3(mp3_file, ID3=ID3)

    # 检查是否已经嵌入了歌词
    if audio.tags and any(isinstance(tag, USLT) for tag in audio.tags.values()):
        print(f"{mp3_file} 已经包含歌词，不需要处理。")
        return

    # 尝试读取 LRC 文件中的歌词
    lyrics = read_lyrics(lrc_file)

    # 嵌入歌词到 MP3 文件
    try:
        audio.add_tags()
    except error:
        pass

    ust = USLT(encoding=3, desc=u'Lyrics', text=lyrics)
    audio.tags.add(ust)
    audio.save()
    print(f"已将歌词嵌入到 {mp3_file} 中。")


def read_lyrics(lrc_file):
    try:
        with open(lrc_file, 'r', encoding='utf-8') as f:
            lyrics = f.read()
    except UnicodeDecodeError:
        try:
            with open(lrc_file, 'r', encoding='gbk') as f:
                lyrics = f.read()
        except UnicodeDecodeError:
            with open(lrc_file, 'r', encoding='iso-8859-1') as f:
                lyrics = f.read()
    return lyrics


def process_music_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.flac'):
                flac_file = os.path.join(root, file)
                lrc_file = os.path.splitext(flac_file)[0] + '.lrc'
                audio = FLAC(flac_file)
                if "LYRICS" not in audio:
                    if os.path.exists(lrc_file):
                        embed_lyrics_from_lrc_to_flac(flac_file, lrc_file)
                    else:
                        print(f"未找到 {lrc_file}，跳过 {flac_file}。")
            elif file.endswith('.mp3'):
                mp3_file = os.path.join(root, file)
                lrc_file = os.path.splitext(mp3_file)[0] + '.lrc'
                audio = MP3(mp3_file, ID3=ID3)
                if not (audio.tags and any(isinstance(tag, USLT) for tag in audio.tags.values())):
                    if os.path.exists(lrc_file):
                        embed_lyrics_from_lrc_to_mp3(mp3_file, lrc_file)
                    else:
                        print(f"未找到 {lrc_file}，跳过 {mp3_file}。")


# 指定目标文件夹路径和目标复制文件夹路径
music_folder = r'C:\Users\root\Music\待处理\源文件'
process_music_folder(music_folder)
