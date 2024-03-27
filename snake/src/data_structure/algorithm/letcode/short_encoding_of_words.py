from typing import List
'''
单词数组 words 的 有效编码 由任意助记字符串 s 和下标数组 indices 组成，且满足：
words.length == indices.length
助记字符串 s 以 '#' 字符结尾
对于每个下标 indices[i] ，s 的一个从 indices[i] 开始、到下一个 '#' 字符结束（但不包括 '#'）的 子字符串 恰好与 words[i] 相等
给你一个单词数组 words ，返回成功对 words 进行编码的最小助记字符串 s 的长度
'''
class Solution:
    def minimumLengthEncoding(self, words: List[str]) -> int:
        words.sort(key=lambda i: len(i), reverse=True)
        string = ""
        for item in words:
            if item in string:
                continue
            string = string + item + "#"
        return len(string)


s = Solution()
words: List[str] = ["time", "me", "bell"]
# words: List[str] = ["t"]
encoding = s.minimumLengthEncoding(words)
print(encoding)

