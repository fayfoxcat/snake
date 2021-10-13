from turtle import Turtle, setworldcoordinates, setup, tracer, update

OBSTACLE = '+'
PART_OF_PATH = ''
TRIED = ''
DEAD_END = ''


class Maze:
    def __init__(self, maze_file):
        rows_in_maze = 0
        columns_in_maze = 0
        self.maze_list = []
        for line in maze_file:
            row_list = []
            col = 0
            for ch in line[:-1]:
                row_list.append(ch)
                if ch == 'S':
                    self.startRow = rows_in_maze
                    self.startCol = col
                col = col + 1
            rows_in_maze = rows_in_maze + 1
            self.maze_list.append(row_list)
            columns_in_maze = len(row_list)

        self.rowsInMaze = rows_in_maze
        self.columnsInMaze = columns_in_maze
        self.xTranslate = -columns_in_maze / 2
        self.yTranslate = rows_in_maze / 2
        self.t = Turtle(shape='turtle')
        setup(width=600, height=600)
        setworldcoordinates(-(columns_in_maze - 1) / 2 - 0.5, (rows_in_maze - 1) / 2 - 0.5,
                            (columns_in_maze - 1) / 2 + 0.5, (rows_in_maze - 1) / 2 + 0.5)

    def draw_maze(self):
        for y in range(self.rowsInMaze):
            for x in range(self.columnsInMaze):
                if self.maze_list[y][x] == OBSTACLE:
                    self.draw_centered_box(x + self.xTranslate, - y + self.yTranslate, 'tan')
        self.t.color('black', 'blue')

    def draw_centered_box(self, x, y, color):
        tracer(0)
        self.t.up()
        self.t.goto(x - .5, y - .5)
        self.t.color('black', color)
        self.t.setheading(90)
        self.t.down()
        self.t.begin_fill()
        for i in range(4):
            self.t.forward(1)
            self.t.right(90)
        self.t.end_fill()
        update()
        tracer(1)

    def move_turtle(self, x, y):
        self.t.up()
        self.t.setheading(self.t.towards(x + self.xTranslate, - y + self.yTranslate))
        self.t.goto(x + self.xTranslate, -y + self.yTranslate)

    def drop_breadcrumb(self, color):
        self.t.dot(color)

    def update_position(self, row, col, val=None):
        if val:
            self.maze_list[row][col] = val
        self.move_turtle(col, row)

        if val == PART_OF_PATH:
            color = 'green'
        elif val == OBSTACLE:
            color = 'red'
        elif val == TRIED:
            color = 'black'
        elif val == DEAD_END:
            color = 'red'
        else:
            color = None
        if color:
            self.drop_breadcrumb(color)

    def is_exit(self, row, col):
        return row == 0 or row == self.rowsInMaze - 1 or col == 0 or col == self.columnsInMaze - 1

    def __getitem__(self, idx):
        return self.maze_list[idx]


# 迷宫搜索函数
def search_from(maze, start_rom, start_column):
    maze.update_position(start_rom, start_column)
    # 检查基本情况
    # 遇到障碍
    if maze[start_rom][start_column] == OBSTACLE:
        return False
    # 遇到经过的轨迹
    if maze[start_rom][start_column] == TRIED:
        return False
    # 找到出口
    if maze.is_exit(start_rom, start_column):
        maze.update_position(start_rom, start_column, PART_OF_PATH)
        return True
    maze.update_position(start_rom, start_column, TRIED)
    # 否则，依次尝试向四个方向移动
    found = search_from(maze, start_rom - 1, start_column) or \
            search_from(maze, start_rom + 1, start_column) or \
            search_from(maze, start_rom, start_column - 1) or \
            search_from(maze, start_rom, start_column + 1)
    if found:
        maze.update_position(start_rom, start_column, PART_OF_PATH)
    else:
        maze.update_position(start_rom, start_column, DEAD_END)
    return found


# 使用
data = [['+', '+', '+', '+', '+', '+', '+', '+', '+', '+', '+'],
        ['+', ' ', ' ', ' ', ' ', ' ', ' ', '+', ' ', ' ', ' '],
        ['+', ' ', '+', ' ', '+', '+', ' ', '+', ' ', '+', '+'],
        ['+', ' ', '+', ' ', ' ', ' ', ' ', '+', ' ', '+', '+'],
        ['+', '+', '+', ' ', '+', '+', ' ', '+', ' ', ' ', '+'],
        ['+', ' ', ' ', ' ', '+', '+', ' ', ' ', ' ', ' ', '+'],
        ['+', ' ', '+', '+', '+', '+', '+', '+', '+', ' ', '+'],
        ['+', ' ', ' ', ' ', '+', '+', ' ', ' ', '+', ' ', '+'],
        ['+', ' ', '+', '+', ' ', ' ', '+', ' ', ' ', ' ', '+'],
        ['+', ' ', ' ', ' ', ' ', ' ', '+', ' ', '+', '+', '+'],
        ['+', '+', '+', '+', '+', '+', '+', ' ', '+', '+', '+']]

c_maze = Maze(data)
search_from(c_maze, 8, 5)
