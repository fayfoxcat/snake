from turtle import Turtle

my_turtle = Turtle()
my_turtle.speed(0)
my_turtle.pu()
my_turtle.right(90)
my_turtle.forward(200)
my_turtle.left(180)
my_turtle.pd()
my_win = my_turtle.getscreen()


# 绘制螺旋线
def draw_spiral(tortoise, line_len):
    if line_len > 0:
        tortoise.forward(line_len)
        tortoise.right(90)
        draw_spiral(tortoise, line_len - 5)


# 绘制树形图
def tree(branch_len, t):
    if branch_len > 5:
        t.forward(branch_len)
        t.right(20)
        tree(branch_len - 15, t)
        t.left(40)
        tree(branch_len - 10, t)
        t.right(20)
        t.backward(branch_len)


# draw_spiral(my_turtle, 100)

tree(100, my_turtle)
my_win.exitonclick()
