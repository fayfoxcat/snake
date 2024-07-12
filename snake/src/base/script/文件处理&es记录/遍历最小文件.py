import os
import heapq


def get_files_with_size(directory):
    files_with_size = []
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                filesize = os.path.getsize(filepath)
                files_with_size.append((filesize, filepath))
            except OSError as e:
                print(f"Error getting size for file {filepath}: {e}")
    return files_with_size


def find_smallest_files(directory, n=5):
    files_with_size = get_files_with_size(directory)
    smallest_files = heapq.nsmallest(n, files_with_size, key=lambda x: x[0])
    return smallest_files


if __name__ == "__main__":
    directory = r'C:\Users\root\Desktop\data\ciphertext'
    smallest_files = find_smallest_files(directory)

    print("The smallest files are:")
    for size, filepath in smallest_files:
        print(f"{filepath}: {size} bytes")

