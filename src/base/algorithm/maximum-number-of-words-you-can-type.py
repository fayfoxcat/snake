"""
1935. 可以输入的最大单词数
键盘出现了一些故障，有些字母键无法正常工作。而键盘上所有其他键都能够正常工作。
给你一个由若干单词组成的字符串 text ，单词间由单个空格组成（不含前导和尾随空格）；
另有一个字符串 brokenLetters ，由所有已损坏的不同字母键组成，返回你可以使用此键盘完全输入的 text 中单词的数目。
"""
from typing import List


class Solution:
    def canBeTypedWords(self, text: str, brokenLetters: str) -> int:
        count = 0
        array: List[str] = text.split()
        brokenLetter: set[str] = set(brokenLetters)
        for item in array:
            count = count + (0 if [i for i in brokenLetter if i in item] else 1)
        return count

    def canBeTypedWords_1(self, text: str, brokenLetters: str) -> int:
        return len([item for item in text.split() if not [i for i in set(brokenLetters) if i in item]])

    def canBeTypedWords_2(self, text: str, brokenLetters: str) -> int:
        bset: set[str] = set(brokenLetters)
        words = text.split()
        res = 0
        for word in words:
            ok = True
            for c in word:
                if c in bset:
                    ok = False
                    break
            if ok == True:
                res += 1
        return res


solution = Solution()
a_text: str = "a b c d e"
a_brokenLetters: str = 'abcde'
print(solution.canBeTypedWords_1(a_text, a_brokenLetters))
