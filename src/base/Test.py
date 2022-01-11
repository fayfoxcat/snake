def brute_force(S, P):
    for i in range(len(S) - len(P) + 1):
        if S[i:i + len(P)] == P:
            print(f'pos = {i}')


s_S = 'AAAAAABC'
s_P = 'AAAB'

brute_force(s_S, s_P)
