import os

from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import APIC, ID3, PictureType, error
from PIL import Image
import io


def compress_image(image_path, max_size=256, quality=85):
    """压缩图片到指定的最大尺寸和质量"""
    with Image.open(image_path) as img:
        # 如果图片是RGBA模式，转换为RGB
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # 保持图片比例
        img.thumbnail((max_size, max_size))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=quality)
        return img_byte_arr.getvalue()


def replace_cover(audio_path, image_path):
    # 读取并压缩图片
    compressed_image_data = compress_image(image_path)

    if audio_path.lower().endswith('.flac'):
        audio = FLAC(audio_path)
        image = Picture()
        image.type = PictureType.COVER_FRONT
        image.mime = 'image/jpeg'
        image.data = compressed_image_data
        audio.clear_pictures()
        audio.add_picture(image)
        audio.save()
    elif audio_path.lower().endswith('.mp3'):
        audio = MP3(audio_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass
        image = APIC(
            encoding=3,
            mime='image/jpeg',
            type=PictureType.COVER_FRONT,
            desc='Cover',
            data=compressed_image_data
        )
        audio.tags.add(image)
        audio.save()

def process_directory(directory):
    # 遍历目录中的所有文件
    for file in os.listdir(directory):
        if file.lower().endswith(('.flac', '.mp3')):
            audio_path = os.path.join(directory, file)
            base_name = os.path.splitext(file)[0]
            image_path = os.path.join(directory, f"{base_name}.jpg")

            # 检查是否存在同名的JPG文件
            if os.path.exists(image_path):
                print(f"Replacing cover for {audio_path} with {image_path}")
                replace_cover(audio_path, image_path)
            else:
                print(f"No matching JPG found for {audio_path}")

# 使用示例
process_directory(r"C:\Users\root\Desktop\Tmp")
