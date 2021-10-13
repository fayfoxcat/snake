# 找零算法
def rec_mc(coin_list, change):
    min_coins = change
    if change in coin_list:
        return 1
    else:
        for i in [c for c in coin_list if c <= change]:
            numbers = 1 + rec_mc(coin_list, change - i)
            if numbers < min_coins:
                min_coins = numbers
    return min_coins


# 使用
d_coin_list = [1, 5, 10, 25]
d_change = 63
print(rec_mc(d_coin_list, d_change))
