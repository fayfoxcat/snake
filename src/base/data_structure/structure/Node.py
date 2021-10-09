class Node:
    def __init__(self, init_data):
        self.init_data = init_data
        self.next = None

    def get_data(self):
        return self.init_data

    def set_data(self, new_data):
        self.init_data = new_data

    def get_next(self):
        return self.next

    def set_next(self, new_node):
        self.next = new_node
