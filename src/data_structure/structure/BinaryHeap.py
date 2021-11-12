class BinaryHeap:
    def __init__(self):
        self.heap_list = [0]
        self.current_size = 0

    def perceive_up(self, i):
        while i // 2 > 0:
            if self.heap_list[i] < self.heap_list[i // 2]:
                tmp = self.heap_list[i // 2]
                self.heap_list[i // 2] = self.heap_list[i]
                self.heap_list[i] = tmp
            i = i // 2

    def perceive_down(self, item):
        while (item * 2) <= self.current_size:
            mc = self.min_child(item)
            if self.heap_list[item] > self.heap_list[mc]:
                tmp = self.heap_list[mc]
                self.heap_list[item] = self.heap_list[mc]
                self.heap_list[item] = tmp
            item = mc

    def min_child(self, item):
        if item * 2 + 1 > self.current_size:
            return item * 2
        else:
            if self.heap_list[item * 2] < self.heap_list[item * 2 + 1]:
                return item * 2
            else:
                return item * 2 + 1

    def insert(self, value):
        self.heap_list.append(value)
        self.current_size = self.current_size + 1
        self.perceive_up(self.current_size)
