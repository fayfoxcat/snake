from math import inf
from typing import List

'''
1937. 扣分后的最大得分
给你一个 m x n 的整数矩阵 points （下标从 0 开始）。一开始你的得分为 0 ，你想最大化从矩阵中得到的分数。
你的得分方式为：每一行 中选取一个格子，选中坐标为 (r, c) 的格子会给你的总得分 增加 points[r][c] 。
然而，相邻行之间被选中的格子如果隔得太远，你会失去一些得分。对于相邻行 r 和 r + 1 （其中 0 <= r < m - 1），
选中坐标为 (r, c1) 和 (r + 1, c2) 的格子，你的总得分 减少 abs(c1 - c2) 。请你返回你能得到的 最大 得分。
'''


class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        m = len(points)
        n = len(points[0])
        dp = points[0]
        for i in range(1, m):
            new_dp = list(dp)
            left_max = -inf
            right_max = -inf
            for j in range(n):
                left_max = max(left_max, dp[j] + j)
                right_max = max(right_max, dp[n - 1 - j] - (n - 1 - j))
                new_dp[j] = max(left_max - j + points[i][j], new_dp[j])
                new_dp[n - 1 - j] = max((n - 1 - j) + right_max + points[i][n - 1 - j], new_dp[n - 1 - j])
            dp = new_dp
            print(new_dp)
        return max(dp)


solution = Solution()
a_points: List[List[int]] = [[6, 8, 0, 4, 4, 3, 6],
                             [9, 9, 1, 5, 7, 7, 7],
                             [1, 3, 8, 7, 2, 1, 1],
                             [4, 8, 1, 1, 9, 5, 1],
                             [3, 1, 4, 3, 3, 2, 0],
                             [0, 3, 7, 9, 1, 7, 6]]
print(solution.maxPoints(a_points))
