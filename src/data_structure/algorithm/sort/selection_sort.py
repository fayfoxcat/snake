def selection_sort(array):
    n = len(array)
    for i in range(n):
        min_value = array[i]
        position = i
        for j in range(i, n - 1):
            if array[j] < min_value:
                min_value = array[j]
                position = j
        array[position] = array[i]
        array[i] = min_value


arr = [64, 34, 25, 12, 22, 11, 90]

selection_sort(arr)

for item in arr:
    print("%d" % item)
