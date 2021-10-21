def insertion_sort(array):
    for i in range(1, len(array)):
        position = i
        insert_value = array[i]
        while position > 0 and array[position - 1] > insert_value:
            array[position] = array[position - 1]
            position = position - 1
        array[position] = insert_value


arr = [9, 34, 25, 12, 22, 11, 90]

insertion_sort(arr)

for item in arr:
    print("%d" % item)
