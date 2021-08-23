from typing import List
"""
821. 字符的最短距离
给你一个字符串 s 和一个字符 c ，且 c 是 s 中出现过的字符。
返回一个整数数组 answer ，其中 answer.length == s.length 且 answer[i] 是 s 中从下标 i 到离它 最近 的字符 c 的 距离 。
两个下标 i 和 j 之间的 距离 为 abs(i - j) ，其中 abs 是绝对值函数。
"""

class Solution:
    def shortestToChar(self, s: str, c: str) -> List[int]:
        answer: List[int] = []
        str_array = list(s)
        for index in range(len(str_array)):
            tmp: List[int] = []
            for index2 in range(len(str_array)):
                if c == (str_array[index2]):
                    tmp.append(abs(index2 - index))
                else:
                    continue
            answer.append(min(tmp))
        return answer

    def shortestToChar_2(self, s: str, c: str) -> List[int]:
        c_pos = [i for i in range(len(s)) if c == s[i]]
        return [min(abs(x - i) for i in c_pos) for x in range(len(s))]

    def shortestToChar_3(self, s: str, c: str) -> List[int]:
        answer: List[int] = []
        c_pos: List[int] = []
        for i in range(len(s)):
            if c == s[i]:
                c_pos.append(i)
        for x in range(len(s)):
            tmp: List[int] = []
            for i in c_pos:
                tmp.append(abs(x-i))
            answer.append(min(tmp))
        return answer

    def shortestToChar_4(self, s: str, c: str) -> List[int]:
        # 定义变量 left记录上一个c的位置，如果存在的话
        left = right_cnt = 0
        answer = [0]*len(s)
        # 循环，找c，计算距离
        for right in range(len(s)):   # 右指针从0遍历到len(s)-1
            if s[right] == c:   # 如果右指针指向的字符是c，那么计算一次距离
                if not right_cnt:   # 如果右指针第一次更新，说明在c的一侧
                    answer[left:right+1] = [abs(right-i) for i in range(left, right+1)]
                else:   # 如果右指针不是第一次更新，说明在两个c中间
                    answer[left:right+1] = [min(abs(right-i), abs(i-left)) for i in range(left, right+1)]
                # 更新左指针以及出现c的次数
                left = right
                right_cnt += 1
            else:
                # 注意这个条件判断要在else里面，以排除最后一个元素是c的情况
                if right == len(s)-1:
                    answer[left:right+1] = [abs(left-i) for i in range(left, right+1)]
        return answer

    def shortestToChar_5(self, s, c):
        prev = float('-inf')
        ans: List[int] = []
        for i, x in enumerate(s):
            if x == c: prev = i
            ans.append(i - prev)

        prev = float('inf')
        for i in range(len(s) - 1, -1, -1):
            if s[i] == c: prev = i
            ans[i] = min(ans[i], prev - i)
        return ans

solution = Solution()
actual_s: str = 'loveleetcode'
actual_c: str = 'e'
# print(solution.shortestToChar(actual_s, actual_c))


# print(solution.shortestToChar_2(actual_s, actual_c))


# print(solution.shortestToChar_3(actual_s, actual_c))


print(solution.shortestToChar_5(actual_s, actual_c))
