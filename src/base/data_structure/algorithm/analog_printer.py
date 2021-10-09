import random

# 模拟打印机
from src.base.data_structure.Queue import Queue


class Printer:
    # 初始化打印机
    def __init__(self, ppm):
        self.page_rate = ppm
        self.current_task = None
        self.time_remaining = 0

    # 打印机工作过程
    def tick(self):
        self.time_remaining = self.time_remaining - 1
        if self.time_remaining <= 0:
            self.current_task = None

    # 检查打印机是否繁忙状态
    def busy(self):
        if self.current_task is not None:
            return True
        else:
            return False

    # 开始下个任务
    def next_task(self, new_task):
        self.current_task = new_task
        self.time_remaining = new_task.get_pages() * 60 / self.page_rate


# 打印任务
class Task:
    # 初始化一个任务
    def __init__(self, time):
        self.time_stamp = time
        self.pages = random.randrange(1, 21)

    # 获取当前打印任务时常
    def get_time(self):
        return self.time_stamp

    # 获取当前打印任务页数
    def get_pages(self):
        return self.pages

    # 等待时间
    def wait_time(self, current_time):
        return current_time - self.time_stamp


# 模拟每一秒可能存在新的打印任务
def new_print_task():
    num = random.randrange(1, 181)
    if num == 180:
        return True
    else:
        return False


def simulation(num_seconds: int, pages_per_minute: int):
    """
    计算平均等待时间
    :param num_seconds: 指定时间范围
    :param pages_per_minute: 打印机打印速率
    :return: 返回平均等待时常
    """
    # 初始化打印机
    lab_printer = Printer(pages_per_minute)
    # 初始化打印队列
    print_queue = Queue()
    # 所有任务等待时常列表
    wait_times = []

    # 模拟指定时间内打印机执行
    for current_second in range(num_seconds):
        if new_print_task():
            task = Task(current_second)
            print_queue.enqueue(task)

        # 当打印机不繁忙且等待队列不空时执行打印任务，保存等待时间
        if (not lab_printer.busy()) and (not print_queue.is_empty()):
            next_task = print_queue.dequeue()
            wait_times.append(next_task.wait_time(current_second))
            lab_printer.next_task(next_task)

        lab_printer.tick()
    if not wait_times:
        print("当前没有打印任务，无法模拟平均等待时常")
    else:
        print("平均等待时常：" + str(round(sum(wait_times) / len(wait_times), 2))
              + " 剩余未执行任务：" + str(print_queue.size()))


s_num_seconds = 3600
s_pages_per_minute = 10
for i in range(10):
    simulation(s_num_seconds, s_pages_per_minute)
