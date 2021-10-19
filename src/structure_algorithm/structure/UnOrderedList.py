from src.structure_algorithm.structure.Node import Node

"""
无序链表实现
"""


class UnOrderedList:
    def __init__(self):
        self.head = None

    def is_empty(self):
        return self.head is None

    def length(self):
        count = 0
        p = self.head
        while p is not None:
            count = count + 1
            p = p.get_next()
        return count

    def search(self, item):
        current = self.head
        flag = False
        while current is not None and not flag:
            if current.get_data() == item:
                flag = True
            else:
                current = current.get_next()
        return flag

    def index(self, item):
        current = self.head
        count = 0
        while current is not None:
            if current.get_data() == item:
                return count
            count = count + 1
            current = current.get_next()
        return None

    def add(self, item):
        node = Node(item)
        node.set_next(self.head)
        self.head = node

    def append(self, item):
        node = Node(item)
        current = self.head
        while True:
            if self.head is None:
                node.set_next(self.head)
                self.head = node
                break
            elif current.get_next() is None:
                current.set_next(node)
                break
            current = current.get_next()

    def insert(self, index, item):
        node = Node(item)
        current = self.head
        while True:
            if current is None or index <= 0:
                node.set_next(self.head)
                self.head = node
                break
            elif current.get_next() is None or index == 1:
                node.set_next(current.get_next())
                current.set_next(node)
                break
            index = index - 1
            current = current.get_next()

    def remove(self, item, **keys):
        previous = None
        current = self.head
        flag = False
        while current is not None and (not flag or keys.get('all')):
            if current.get_data() == item:
                if previous is None:
                    self.head = current.get_next()
                else:
                    previous.set_next(current.get_next())
                flag = True
            else:
                previous = current
            current = current.get_next()

    def pop(self, index):
        previous = None
        current = self.head
        while (self.head and current.get_next()) is not None:
            if previous is None and index == 0:
                self.head = current.get_next()
                break
            if index == 0:
                previous.set_next(current.get_next())
                break
            index = index - 1
            previous = current
            current = current.get_next()

    def print(self):
        current = self.head
        nodes = []
        while current is not None:
            nodes.append(current.get_data())
            current = current.get_next()
        print(nodes)
