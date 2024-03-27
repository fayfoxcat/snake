from typing import List


def merge_sort(array: List):
    print("分组", array)
    if len(array) > 1:
        mid_index = len(array) // 2
        left_array = array[:mid_index]
        right_array = array[mid_index:]

        merge_sort(left_array)
        merge_sort(right_array)

        i = 0
        j = 0
        k = 0
        while i < len(left_array) and j < len(right_array):
            if left_array[i] < right_array[j]:
                array[k] = left_array[i]
                i = i + 1
            else:
                array[k] = right_array[j]
                j = j + 1
            k = k + 1

        while i < len(left_array):
            array[k] = left_array[i]
            i = i + 1
            k = k + 1

        while j < len(right_array):
            array[k] = right_array[j]
            j = j + 1
            k = k + 1

        print("合并：", array)


arr = [9, 34, 25, 12, 22, 11, 90]
merge_sort(arr)
for item in arr:
    print("%d" % item)
