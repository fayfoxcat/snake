from src.structure_algorithm.structure import Stack

'''
匹配符号
'''
def matches(open, close):
    opens = "([{"
    closers = ")]}"
    return opens.index(open) == closers.index(close)


def match(parentheses: str) -> bool:
    s = Stack()
    flag = True
    index = 0
    while index < len(parentheses) and flag:
        item = parentheses[index]
        if item in "{[(":
            s.push(item)
        else:
            if s.is_empty():
                flag = False
            else:
                top = s.pop()
                flag = matches(top, item)

        index = index + 1

    if flag and s.is_empty():
        return True
    else:
        return False


print(match("(){[([])]}()"))
