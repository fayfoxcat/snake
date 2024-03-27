def shell_sort(array):
    sublist_count = len(array) // 2
    while sublist_count > 0:
        for start_position in range(sublist_count):
            gap_insert_sort(array, start_position, sublist_count)
            print("After increments of size", sublist_count, "The list is", array)
        sublist_count = sublist_count // 2


def gap_insert_sort(array, start, gap):
    for i in range(start + gap, len(array), gap):
        position = i
        insert_value = array[i]
        while position > 0 and array[position - gap] > insert_value:
            array[position] = array[position - gap]
            position = position - gap
        array[position] = insert_value


arr = [9, 34, 25, 12, 22, 11, 90]

shell_sort(arr)

for item in arr:
    print("%d" % item)
