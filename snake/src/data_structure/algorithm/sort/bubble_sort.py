def bubble_sort(array):
    n = len(array)
    for item in range(n):
        for j in range(0, n - item - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]


arr = [64, 34, 25, 12, 22, 11, 90]

bubble_sort(arr)

print("排序后的数组:")
for i in range(len(arr)):
    print("%d" % arr[i]),
