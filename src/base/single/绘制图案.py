import turtle
from typing import List

# 设置窗口信息
turtle.title("绘制椭圆")
turtle.setup(2360, 1240, 70, 50)
turtle.screensize(2560, 1440, bg='white')
turtle.color('yellow', 'orange')

# 坐标集合
points: List[List[int]] = [[-500, 100], [-400, 200], [-300, 300], [-200, 400], [-100, 500],
                           [100, 500], [200, 400], [300, 300], [400, 200], [500, 100],
                           [500, -100], [400, -200], [300,-300], [200, -400], [100, -500],
                           [-100, -500], [-200, -400], [-300, -300], [-400, -200], [-500, 100]]
# 生成随机坐标
# for i in range(20):
#     x = random.randint(-1180, 1180)
#     y = random.randint(-720, 720)
#     points.append([x, y])
# points.append(points[0])

# 画笔
pen = turtle.Turtle()

while points[0] != points[int(len(points) / 2)]:
    # 计算新节点
    s = points[1]
    t = points[1]
    for i in range(len(points)):
        if i == len(points) - 1:
            points[i][0] = int((t[0] + s[0]) / 2)
            points[i][1] = int((t[1] + s[1]) / 2)
        else:
            points[i][0] = int((t[0] + points[i + 1][0]) / 2)
            points[i][1] = int((t[1] + points[i + 1][1]) / 2)
            t = points[i + 1]
    # 绘制
    pen.reset()
    for i in range(len(points)):
        if i == 0:
            pen.up()
            pen.goto(points[i][0], points[i][1])
            pen.down()
        else:
            pen.goto(points[i][0], points[i][1])

# 暂停
turtle.done()
