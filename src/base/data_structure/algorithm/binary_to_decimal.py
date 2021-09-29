from Stack import Stack

"""
十进制转其他进制进制
"""


def solution(scale: int, value: int) -> str:
    number: str = '0123456789ABCDEF'
    binary: str = ''
    stack = Stack()
    while value > 0:
        stack.push(int(value % scale))
        value = int(value / scale)

    while stack.size() > 0:
        binary = binary + number[stack.pop()]
    return binary


s_scale: int = 16
v_value: int = 1200
print(solution(s_scale, v_value))
