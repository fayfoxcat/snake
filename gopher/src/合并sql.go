package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

const dirPath = "C:/Users/root/Desktop/SQL脚本处理/原始数据/精简数据/"
const outFilePath = "C:/Users/root/Desktop/SQL脚本处理/结果数据/结果.sql"

func main() {
	start := time.Now()

	// 读取文件夹下的所有文件
	files, _ := os.ReadDir(dirPath)
	var wg sync.WaitGroup
	outfile, _ := os.Create(outFilePath)
	defer outfile.Close()

	for _, f := range files {
		wg.Add(1)
		go func(f os.DirEntry) {
			defer wg.Done()
			processFile(f, outfile)
		}(f)
	}
	wg.Wait()

	fmt.Printf("运行时间: %s\n", time.Since(start))
}

func processFile(f os.DirEntry, outfile *os.File) {
	file, _ := os.Open(filepath.Join(dirPath, f.Name()))
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var sb strings.Builder
	counter := 0
	prefix := ""
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "INSERT INTO") {
			if counter == 5000 {
				outfile.WriteString(sb.String() + ";\n")
				sb.Reset()
				counter = 0
			}
			if counter == 0 {
				prefix, line = splitInsert(line)
				sb.WriteString(prefix + line + ",")
			} else {
				_, line = splitInsert(line)
				sb.WriteString(line + ",")
			}
			counter++
		}
	}
	if sb.Len() > 0 {
		outfile.WriteString(strings.TrimSuffix(sb.String(), ",") + ";\n")
	}
}

func splitInsert(line string) (string, string) {
	parts := strings.SplitN(line, "VALUES ", 2)
	return parts[0] + "VALUES ", parts[1][:len(parts[1])-1]
}
