from typing import List


class Solution:
    def maxSubArrayLen(self, nums: List[int], k: int) -> int:
        max = 0
        for i, item in enumerate(nums):
            sum = 0  
            tmp = 1
            for j in nums[i:]:
                sum += j
                tmp = tmp + 1
                if sum == k:
                    break
            if tmp > max and sum == k:
                max = tmp
        return max


solution = Solution()
a_rungs: List[int] = [-2, -1, 2, 1]
a_dist: int = 1
print(solution.maxSubArrayLen(a_rungs, a_dist))
