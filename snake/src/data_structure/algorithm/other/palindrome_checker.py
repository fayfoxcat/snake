from src.data_structure.structure import Deque


def palindrome_checker(s: str) -> bool:
    """
    回文检测器
    :param s: 待检测字符串
    :return: 校验结果
    """
    flag: bool = True
    deque = Deque()
    for item in s:
        deque.add_front(item)
    while deque.size() > 1 and flag:
        if deque.remove_front() != deque.remove_rear():
            flag = False
    return flag


print(palindrome_checker("toot"))
