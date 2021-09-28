"""
十进制转二进制
"""
from typing import List

from Stack import Stack


def solution(value: int) -> int:
    binary: str = "0"
    stack = Stack()
    while value > 0:
        stack.push(int(value % 2))
        value = int(value / 2)

    while stack.size() > 0:
        binary = binary + str(stack.pop())
    return int(binary)


print(solution(120))
