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
        values = self.recursion(points, 0, 0, 0)
        return max(values)

    # 递归计算(时间复杂度过高，不建议使用)
    def recursion(self, part, index, pre, value) -> set[int]:
        collect = set()
        if index < len(part):
            for i, item in enumerate(part[index]):
                poor = 0 if index == 0 else abs(pre - i)
                collect.update(self.recursion(part, index + 1, i, value + item - poor))
                if index == len(part) - 1:
                    collect.add(value + item - poor)
        return collect

    # 双重遍历(动态转移方程，动态规划)
    def double_cycle(self, points: List[List[int]]) -> int:
        # f[i][j]=max{f[i−1][j′]−∣j−j′∣}+points[i][j]
        m, n = len(points), len(points[0])
        f = [0] * n
        for i in range(m):
            g = [0] * n
            best = float("-inf")
            # 正序遍历
            for j in range(n):
                best = max(best, f[j] + j)
                g[j] = max(g[j], best + points[i][j] - j)

            best = float("-inf")
            # 倒序遍历
            for j in range(n - 1, -1, -1):
                best = max(best, f[j] - j)
                g[j] = max(g[j], best + points[i][j] + j)
            f = g
        return max(f)


solution = Solution()
a_points: List[List[int]] = [[6, 8, 0],
                             [9, 9, 1],
                             [1, 3, 8]]
# print(solution.maxPoints(a_points))
print(solution.double_cycle(a_points))
