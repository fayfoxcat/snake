from typing import List

from src.structure_algorithm.structure import Queue

'''
在模拟传土豆的过程中，程序将这个孩子的名字移出队列，然后立刻将其插入队列的尾部。随后，
这个孩子会一直等待，直到再次到达队列的头部。在出列和入列num 次之后，此时位于队列头部
的孩子出局，新一轮游戏开始。如此反复，直到队列中只剩下一个名字（队列的大小为1）。
'''


def potato_game(child: List[str], num: int) -> str:
    queue = Queue()
    for item in child:
        queue.enqueue(item)

    while queue.size() > 1:
        for index in range(num):
            queue.enqueue(queue.dequeue())
        queue.dequeue()
    return queue.dequeue()


s_child: List[str] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'G', 'K', 'L', 'M',
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
s_num: int = 5
print(potato_game(s_child, s_num))
