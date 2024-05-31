import os
import shutil
import zipfile
import re
from concurrent.futures import ThreadPoolExecutor


# 遍历源目录中的所有文件
def copy_file(source_file, target_file, target_folder):
    # 检查目标文件夹是否存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    # 复制文件
    shutil.copy(source_file, target_file)
    print(f"文件 {os.path.basename(source_file)} 已复制到 {target_folder}")


# 多线程操作
def copy_files(source_dir, target_root_dir):
    # 获取所有需要处理的文件
    files_to_copy = []
    for filename in os.listdir(source_dir):
        if filename.endswith("_DQ.WPD"):
            parts = filename.split('_')
            if len(parts) == 4:
                folder_name = parts[0]
                date_folder = parts[1]
                # 构建目标文件夹路径
                target_folder = os.path.join(target_root_dir, folder_name, date_folder)
                # 构建完整的源文件路径和目标文件路径
                source_file = os.path.join(source_dir, filename)
                target_file = os.path.join(target_folder, filename)
                files_to_copy.append((source_file, target_file, target_folder))
            else:
                print(f"文件名 {filename} 格式不正确。")
        else:
            print(f"文件 {filename} 不符合预期的后缀。")

    # 使用 ThreadPoolExecutor 来进行多线程复制
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(copy_file, source_file, target_file, target_folder) for
                   source_file, target_file, target_folder in files_to_copy]
        for future in futures:
            future.result()


# 单线程压缩
def compress_folder(folder_path, target_root_dir):
    # 假设每个文件夹下都有一个子文件夹，且该子文件夹名为date_folder（年月）
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    if subfolders:
        # 获取第一个子文件夹名作为 date_folder
        date_folder = subfolders[0]
        # 提取年月信息
        year_month = date_folder[:6]
        # 创建一个压缩文件，名称为 folder_name + 年月
        folder_name = os.path.basename(folder_path)
        zip_filename = os.path.join(target_root_dir, f"{folder_name}{year_month}.zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for subfolder in subfolders:
                subfolder_path = os.path.join(folder_path, subfolder)
                for root, _, files in os.walk(subfolder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)
        print(f"文件夹 {folder_path} 已压缩为 {zip_filename}")


# 多线程压缩
def compress_folders(target_root_dir, folders_to_compress=None):
    # 获取所有需要处理的文件夹
    all_folders = [os.path.join(target_root_dir, folder_name) for folder_name in os.listdir(target_root_dir)
                   if os.path.isdir(os.path.join(target_root_dir, folder_name)) and
                   (folders_to_compress is None or folder_name in folders_to_compress)]

    # 使用 ThreadPoolExecutor 来进行多线程压缩
    with ThreadPoolExecutor() as executor:
        # 提交每个文件夹压缩任务
        futures = [executor.submit(compress_folder, folder_path, target_root_dir) for folder_path in all_folders]
        # 等待所有任务完成
        for future in futures:
            future.result()


# 规则压缩文件
def compress_files_by_patterns(target_path, prefix_patterns):
    # 获取目标路径下的所有文件
    files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]

    for prefix_pattern in prefix_patterns:
        # 创建一个字典用于存储匹配的文件
        file_groups = {}

        # 匹配文件并分组
        for file in files:
            match = re.match(rf"({prefix_pattern})_(\d{{6}})\d{{2}}_(\d{{4}})_DQ\.WPD", file)
            if match:
                prefix = match.group(1)
                date = match.group(2)[:6]  # 只取到月份
                key = f"{prefix}_{date}_DQ"

                if key not in file_groups:
                    file_groups[key] = []
                file_groups[key].append(file)

        # 压缩文件
        for group, group_files in file_groups.items():
            zip_file_path = os.path.join(target_path, f"{group}.zip")
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for file in group_files:
                    zipf.write(os.path.join(target_path, file), file)


# 定义源文件夹和目标文件夹路径
source_dir = r"C:\Users\root\Desktop\2023年3月\dq202303"
target_root_dir = r"C:\Users\root\Desktop\2023年3月\fileData"
# 确保目标根目录存在
if not os.path.exists(target_root_dir):
    print(f"目标根目录 {target_root_dir} 不存在。")
    exit()

# 示例调用
copy_files(source_dir, target_root_dir)

# 指定需要压缩的文件夹名称列表
statistics_list_1 = ['GHSYFD', 'SFGYFD', 'SNGYFD', 'SCTHFD', 'GYFDFX', 'YZBYFD', 'HYSNFD', 'HRGYFD', 'HRPZFD', 'HZSYFD',
                     'RBDAFF', 'RBDLQF', 'XXCRFD', 'XTGYFD', 'RBZSFD', 'ZDDYFD', 'ZDCJGF', 'GYFDFY', 'YZJHFD', 'XTXYFD',
                     'XXFNFD', 'RNHAFD', 'JHZEGF', 'DTSLFD', 'HZHYFD', 'GHXCGF', 'XXSHFD', 'GHTYFD']
statistics_list_3 = ['GHSYFD', 'GXHHFD', 'GXLHFD', 'GXRHFD', 'SFGYFD', 'SNBYJF', 'SNLSFD', 'SNSYHF', 'SCTHFD', 'GYFDFX',
                     'JSHRFD', 'HNRHFD', 'HRTHFD', 'HZSYFD', 'RBDLQF', 'XTGYFD', 'SXFHFD', 'ZDDYFD', 'ZDCJGF', 'BHFDBT',
                     'JSXSFD', 'CJXHFD', 'YNSHFD', 'GYFDFY', 'XXFNFD', 'SXSHGF', 'RNHAFD', 'GXDZFD', 'GRJHFD', 'GXGYFD',
                     'HNJHFD', 'HZHYFD', 'XXSHFD', 'GHRHFD']

# 压缩指定的文件夹
# compress_folders(target_root_dir, statistics_list_3)

# 压缩指定规则文件
# compress_files_by_patterns(source_dir, folders_to_compress)
