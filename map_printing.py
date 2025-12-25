from typing import List


class MazePrinter:
    def __init__(self, maze: List[List[str]]):
        self.color_path: str = '48;5;232m'
        self.color_wall: str = '48;5;255m'
        self.color_optimal: str = '48;5;m'
        try:
            self.y_axis: int = len(maze)
            self.x_axis: int = len(maze[0])
            self.maze = maze
        except Exception:
            raise ValueError('Invalid Maze format! ' +
                             'Expected [[line 1], [line 2]...]')

    def display_cell(self, cell: str, x: int, y: int):
        for x_brush in range(3):
            for y_brush in range(3):
                abs_x = x_brush + y * 3 + 3
                abs_y = y_brush + x * 5 + 6
                if (x_brush == 0 and y == 0) or (y_brush == 0 and x == 0):
                    color = self.color_wall
                else:
                    color = self.color_path
                print(f"\033[{abs_x};{abs_y}H\033[{color}   \033[0m")
    
    def display_cell_debug(self, cell: str, x: int, y: int):
        for x_brush in range(3):
            for y_brush in range(3):
                abs_x = x_brush + y * 3 + 3
                abs_y = y_brush + x * 5 + 6
                if (x_brush == 0 and y == 0) or (y_brush == 0 and x == 0):
                    color = self.color_wall
                else:
                    color = self.color_path
                print(f"\033[{abs_x};{abs_y}H\033[{color} {cell} \033[0m")
    
    def display_outer_borders(self):
        color = self.color_wall
        for x in range(self.x_axis * 3 + 4):
            for y in range(self.y_axis * 3 + 4):
                if y == self.y_axis * 3 + 3 or x == self.x_axis * 3 + 3:
                    print(f'\033[{x + 3};{y + 6}H\033[{color} \033[0m')

    def display_maze(self):
        for x in range(self.x_axis):
            for y in range(self.y_axis):
                self.display_cell(self.maze[y][x], x, y)
        self.display_outer_borders()
