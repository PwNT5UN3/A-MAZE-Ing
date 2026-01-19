from re import M
from maze_generator.maze_gen import DFSearch, MazeCell
from pprint import pprint


# def dfs(maze: list[list[MazeCell]]) -> None:
#     if maze is None:
#         return


def test() -> None:
    my_gen = DFSearch(width=2, height=2)
    my_maze = my_gen.generate_maze()
    len_of_maze = my_gen.get_size()
    # dfs(my_maze)

    pprint(len_of_maze)


if __name__ == "__main__":
    test()
