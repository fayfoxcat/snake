# 找零算法
from typing import List


def rec_mc(coin_list, change):
    min_coins = change
    if change in coin_list:
        return 1
    else:
        for item in [c for c in coin_list if c <= change]:
            numbers = 1 + rec_mc(coin_list, change - item)
            if numbers < min_coins:
                min_coins = numbers
    return min_coins


# 保存记录的找零算法
def rec_mc_save(coin_list, change, result_list: dict):
    min_coins = change
    if change in coin_list:
        result_list[change] = 1
        return 1
    elif result_list.get(change) is not None:
        return result_list.get(change)
    else:
        for item in [c for c in coin_list if c <= change]:
            numbers = 1 + rec_mc_save(coin_list, change - item, result_list)
            if numbers < min_coins:
                min_coins = numbers
                result_list[change] = min_coins
    return min_coins


# 动态规划
def dp_make_change(coin_list, change):
    min_coins = {}
    for cents in range(change + 1):
        coin_count = cents
        for j in [c for c in coin_list if c <= cents]:
            if min_coins[cents - j] + 1 < coin_count:
                coin_count = min_coins[cents - j] + 1
        min_coins[cents] = coin_count
    return min_coins[change]


# 动态规划:记录各类硬币面值
def dp_make_change_detail(coin_list: List[int], change: int) -> dict:
    # 0-change各找零金额列表
    min_coins: dict = {}
    # 计算每种金额最少使用硬币组合
    for cents in range(change + 1):
        # {面值：额度}
        coin_count: dict = {min(coin_list): cents}
        for j in [c for c in coin_list if c <= cents]:
            if sum(min_coins[cents - j].values()) + 1 < sum(coin_count.values()):
                tmp = min_coins[cents - j].copy()
                tmp[j] = 1 if tmp.get(j) is None else (tmp.get(j) + 1)
                coin_count = tmp
        min_coins[cents] = coin_count
    return min_coins[change]


# 使用
d_coin_list = [1, 5, 10, 25]
d_change = 66
# print(rec_mc(d_coin_list, d_change))
# print(rec_mc_save(d_coin_list, d_change, {}))
# print(dp_make_change(d_coin_list, d_change))
detail = dp_make_change_detail(d_coin_list, d_change)
for key in detail:
    print(str(detail.get(key)) + "枚" + str(key) + "硬币")
