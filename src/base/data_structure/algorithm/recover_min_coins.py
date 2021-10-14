# 找零算法
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
def dp_make_change(coin_list, change, min_coins):
    for cents in range(change + 1):
        coin_count = cents
        for j in [c for c in coin_list if c <= cents]:
            if min_coins[cents - j] + 1 < coin_count:
                coin_count = min_coins[cents - j] + 1
        min_coins[cents] = coin_count
    return min_coins[change]


# 使用
d_coin_list = [1, 5, 10, 25]
d_change = 63
# print(rec_mc(d_coin_list, d_change))
# print(rec_mc_save(d_coin_list, d_change, {}))
print(dp_make_change(d_coin_list, d_change, [0] * 64))
