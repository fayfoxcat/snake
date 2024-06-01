import os
import shutil
from mutagen.flac import FLAC
from PIL import Image
from io import BytesIO

# 定义目录路径
source_dir = r'C:\Users\root\Music\Music'
target_dir = r'C:\Users\root\Music\Music2'

# 如果目标目录不存在，则创建它
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 遍历源目录中的所有文件
for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith('.flac'):
            file_path = os.path.join(root, file)
            try:
                # 读取FLAC文件
                audio = FLAC(file_path)
                cover_found = False
                # 检查封面信息
                if audio.pictures:
                    # 遍历所有封面图片
                    for picture in audio.pictures:
                        # 打开封面图片
                        image = Image.open(BytesIO(picture.data))
                        width, height = image.size
                        size = len(picture.data)
                        # 判断封面图片的分辨率是否小于500px
                        if width < 800 or height < 800:
                            cover_found = True
                            # 打印文件名、分辨率和大小
                            print(f"文件名: {file}, 分辨率: {width}x{height}, 大小: {size} 字节")
                            # 复制文件到目标目录
                            shutil.copy(file_path, target_dir)
                            break
                        else:
                            print(f"文件名: {file}, 分辨率: {width}x{height}, 大小: {size} 字节")
            except Exception as e:
                print(f"处理文件 {file_path} 时发生错误: {e}")
