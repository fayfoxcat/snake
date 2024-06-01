import os
import shutil

# 定义文件夹路径
music_folder = r"C:\Users\root\Music\Music5"
lrc_folder = r"C:\Users\root\Music\lrc"

# 获取music_folder中的所有文件名称（不包含扩展名）
music_files = {os.path.splitext(f)[0] for f in os.listdir(music_folder)}

# 遍历lrc_folder中的文件，匹配同名文件并复制到music_folder
for lrc_file in os.listdir(lrc_folder):
    lrc_name, lrc_ext = os.path.splitext(lrc_file)
    if lrc_name in music_files:
        src_path = os.path.join(lrc_folder, lrc_file)
        dst_path = os.path.join(music_folder, lrc_file)
        shutil.copy2(src_path, dst_path)
        print(f"已复制: {lrc_file} 到 {music_folder}")

print("文件匹配和复制完成。")
