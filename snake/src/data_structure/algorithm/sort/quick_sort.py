def quick_sort(array):
    quick_sort_helper(array, 0, len(array) - 1)


def quick_sort_helper(array, first, last):
    if first < last:
        split_point = partition(array, first, last)
        quick_sort_helper(array, first, split_point - 1)
        quick_sort_helper(array, split_point + 1, last)


def partition(array, first, last):
    # mid_index = (first + last // 2)
    # pivot_value = array[mid_index]
    pivot_value = array[first]
    left_mark = first + 1
    right_mark = last
    done = False
    while not done:
        while left_mark <= right_mark and array[left_mark] <= pivot_value:
            left_mark = left_mark + 1
        while right_mark >= left_mark and array[right_mark] >= pivot_value:
            right_mark = right_mark - 1
        if right_mark < left_mark:
            done = True
        else:
            array[right_mark], array[left_mark] = array[left_mark], array[right_mark]
    array[right_mark], array[first] = array[first], array[right_mark]
    return right_mark


arr = [64, 34, 25, 12, 22, 11, 90]

quick_sort(arr)

for item in arr:
    print("%d" % item)
