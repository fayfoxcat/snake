from turtle import Turtle
from typing import List


def draw_triangle(points: List[tuple[int, int]], color, t: Turtle):
    t.fillcolor(color)
    t.up()
    t.goto(points[0])
    t.down()
    t.begin_fill()
    t.goto(points[1])
    t.goto(points[2])
    t.goto(points[0])
    t.end_fill()


def get_mid(p1: tuple[int, int], p2: tuple[int, int]):
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2


def sierpinski(points: List[tuple[int, int]], degree: int, t: Turtle):
    color_map = ['blue', 'red', 'green', 'white', 'yellow', 'violet', 'orange']
    draw_triangle(points, color_map[degree], t)
    if degree > 0:
        sierpinski([points[0], get_mid(points[0], points[1]), get_mid(points[0], points[2])], degree - 1, t)
        sierpinski([points[1], get_mid(points[0], points[1]), get_mid(points[1], points[2])], degree - 1, t)
        sierpinski([points[2], get_mid(points[0], points[2]), get_mid(points[1], points[2])], degree - 1, t)


my_turtle = Turtle()
my_turtle.speed(0)
my_win = my_turtle.getscreen()
my_points: List[tuple[int, int]] = [(-200, -100), (0, 200), (200, -100)]
sierpinski(my_points, 5, my_turtle)
my_turtle.hideturtle()
my_win.exitonclick()
