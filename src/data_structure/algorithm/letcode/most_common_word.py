import collections
import re
from typing import List


class Solution:
    def mostCommonWord(self, paragraph: str, banned: List[str]) -> str:
        for (a, b) in collections.Counter(re.findall("\w+", paragraph.lower())).most_common():
            if a not in banned:
                return a


s_paragraph: str = "Bob hit a ball, the hit BALL flew far after it was hit."
s_banned: List[str] = ["hit"]

s = Solution()
target_word = s.mostCommonWord(s_paragraph, s_banned)
print(target_word)
