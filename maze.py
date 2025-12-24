import map_printing as mp
from typing import List
from maze_generator import MazeGenerator


class Maze:
    def __init__(self):
        self.maze: List[List[str]] = []
        self.maze_generator = MazeGenerator()
        self.generator()
        print(self.maze)

    def generator(self):
        self.maze_generator.test_maze()


if __name__ == "__main__":
    printer = mp.MazePrinter([[1, 2, 3], [4, 5, 6], [7, 8, 9], ['a', 'b', 'c']])
    printer.display_maze()
