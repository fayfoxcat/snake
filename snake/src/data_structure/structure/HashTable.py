class HashTable:
    def __init__(self):
        self.size = 11
        self.slots = [None] * self.size
        self.data = [None] * self.size

    def get(self, key):
        hash_value = self.hash_function(key, len(self.slots))
        index = hash_value
        while self.slots[hash_value] != key:
            hash_value = self.re_hash(hash_value, len(self.slots))
            if index == hash_value:
                hash_value = index
                break
        return self.data[hash_value]

    def put(self, key, value):
        hash_value = self.hash_function(key, len(self.slots))
        if self.slots[hash_value] is None:
            self.slots[hash_value] = key
            self.data[hash_value] = value
        else:
            if self.slots[hash_value] == key:
                self.data[hash_value] = value
            else:
                next_slot = self.re_hash(hash_value, len(self.slots))
                while self.slots[next_slot] is not None and self.slots[next_slot] != key:
                    next_slot = self.re_hash(next_slot, len(self.slots))
                if self.slots[next_slot] is None:
                    self.slots[next_slot] = key
                    self.data[next_slot] = value
                else:
                    self.data[next_slot] = value

    def hash_function(self, key, size):
        return key % size

    def re_hash(self, old_hash, size):
        return (old_hash + 1) % size

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, data):
        self.put(key, data)
