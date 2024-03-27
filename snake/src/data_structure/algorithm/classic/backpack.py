def abc(capacity: int, items: []) -> [[]]:
    dp = [[0] * (capacity + 1) for _ in range(len(items) + 1)]
    for y in range(1, len(items) + 1):
        value = items[y - 1][0]
        weight = items[y - 1][1]
        for x in range(capacity + 1):
            if x >= weight:
                dp[y][x] = max(dp[y - 1][x], dp[y - 1][x - weight] + value)
            else:
                dp[y][x] = dp[y - 1][x]
    return [dp[-1][-1], getSequence(dp, items)]


def getSequence(knapsackVlaues: [], items: []) -> []:
    sequence = []
    y = len(knapsackVlaues) - 1
    x = len(knapsackVlaues[0]) - 1
    while y > 0 and x > 0:
        if knapsackVlaues[y][x] == knapsackVlaues[y - 1][x]:
            y -= 1
        else:
            sequence.append(items[y - 1])
            x -= items[y - 1][1]
            y -= 1
    return list(reversed(sequence))


abc1 = abc(10, [[1, 2], [4, 3], [5, 6], [6, 7]])
print(abc1)
