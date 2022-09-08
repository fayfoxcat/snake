# def brute_force(S, P):
#     for i in range(len(S) - len(P) + 1):
#         if S[i:i + len(P)] == P:
#             print(f'pos = {i}')
from typing import List


def get_first_letter(s1, s2):
    results = []
    for i1 in s1:
        for i2 in s2:
            result = [i1[0:1], i2[0:2]]
            results.append(result)
    return results


s_1 = ["AUTO", "1-2.412GHZ", "2-"]
s_2 = ["30%", "40%", "50%"]
print(get_first_letter(s_1, s_2))

# s_S = 'AAAAAABC'
# s_P = 'AAAB'
# brute_force(s_S, s_P)
