# 清点法
import timeit


def anagram_by_list(s1, s2):
    alist = list(s2)
    pos1 = 0
    stillOK = True
    while pos1 < len(s1) and stillOK:
        pos2 = 0
        found = False
        while pos2 < len(alist) and not found:
            if s1[pos1] == alist[pos2]:
                found = True
            else:
                pos2 = pos2 + 1
        if found:
            alist[pos2] = None
        else:
            stillOK = False
        pos1 = pos1 + 1
    return stillOK


# 排序法
def anagram_by_sort(s1, s2):
    list1 = list(s1)
    list2 = list(s2)

    list1.sort()
    list2.sort()

    flag = True
    for index, item in enumerate(list1):
        if item != list2[index]:
            flag = False
    return flag


# 计数法
def anagram_by_count(s1, s2):
    c1 = [0] * 26
    c2 = [0] * 26

    for i in range(len(s1)):
        pos = ord(s1[i]) - ord('a')
        c1[pos] = c1[pos] + 1

    for i in range(len(s2)):
        pos = ord(s2[i]) - ord('a')
        c2[pos] = c2[pos] + 1

    flag = True
    i: int = 0
    while i < 26 and flag:
        if c1[i] == c2[i]:
            i = i + 1
        else:
            flag = False
    return flag


# a: str = "aabbcc"
# b: str = "abaccc"
# print(anagram_by_list(a, b))
# print(anagram_by_sort(a, b))
# print(anagram_by_count(a, b))


# def generate_list_1():
#     lists = []
#     for i in range(1000):
#         lists = lists + [i]
#
#
# def generate_list_2():
#     lists = []
#     for i in range(1000):
#         lists.append(i)
#
#
# def generate_list_3():
#     lists = [i for i in range(1000)]
#
#
# def generate_list_4():
#     lists = list(range(1000))
#
#
# t1 = Timer("generate_list_1()", "from __main__ import generate_list_1")
# print("连接 ", round(t1.timeit(number=1000), 5), " 秒")
#
# t2 = Timer("generate_list_2()", "from __main__ import generate_list_2")
# print("追加 ", round(t2.timeit(number=1000), 5), " 秒")
#
# t3 = Timer("generate_list_3()", "from __main__ import generate_list_3")
# print("列表解析 ", round(t3.timeit(number=1000), 5), " 秒")
#
# t4 = Timer("generate_list_4()", "from __main__ import generate_list_4")
# print("列表构造器 ", round(t4.timeit(number=1000), 5), " 秒")

# 测试列表pop()和pop(i)性能
# popzero = Timer("x.pop(0)", "from __main__ import x")
# popend = Timer("x.pop()", "from __main__ import x")
# print("pop(0) pop()")
# for i in range(1000000, 100000001, 1000000):
#     x = list(range(i))
#     pt = popend.timeit(number=1000)
#     x = list(range(i))
#     pz = popzero.timeit(number=1000)
#     print("%15.5f, %15.5f" % (pz, pt))

for i in range(10000, 1000001, 20000):
    t = timeit.Timer("random.randrange(%d) in x" % i, "from __main__ import random, x")
    x = list(range(i))
    lst_time = t.timeit(number=1000)
    x = {j: None for j in range(i)}
    d_time = t.timeit(number=1000)
    print("%d, %10.3f, %10.3f" % (i, lst_time, d_time))
