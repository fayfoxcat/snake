import re

def process_lyrics(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('[') and stripped_line.endswith(']'):
            # This is a timestamp line, keep it as is
            processed_lines.append(stripped_line)
        elif stripped_line.startswith('[') and ']' in stripped_line:
            # This line contains both timestamp and lyrics
            timestamp, lyrics = stripped_line.split(']', 1)
            timestamp += ']'
            # Use regex to split different language parts
            match = re.match(r'([^\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]*[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+[^\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]*)(.*)', lyrics.strip())
            if match:
                first_part = match.group(1).strip()
                second_part = match.group(2).strip()
                processed_lines.append(f"{timestamp} {first_part}\n{timestamp} {second_part}")
            else:
                processed_lines.append(stripped_line)
        else:
            # This is a line with only lyrics (either Korean, Chinese, English, or Japanese)
            processed_lines.append(stripped_line)

    return processed_lines

def main():
    file_path = 'lyrics.lrc'  # Replace with your file path
    processed_lines = process_lyrics(file_path)

    for line in processed_lines:
        print(line)

if __name__ == "__main__":
    main()
