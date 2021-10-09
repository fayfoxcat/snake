from src.base.data_structure.structure.Node import Node


class UnorderedList:
    def __init__(self):
        self.head = None

    def is_empty(self):
        return self.head is None

    def add(self, item):
        node = Node(item)
        node.set_next(self.head)
        self.head = node
