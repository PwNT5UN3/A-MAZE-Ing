from maze_generator.maze_gen import WilsonsAlgorithm
from pprint import pprint

# bad_seeds = 0
# for seed in range(2147483648):
#     gen = WilsonsAlgorithm(10, 15, seed=seed)
#     try:
#         maze = gen.generate_maze()
#     except RecursionError:
#         print(f"seed {seed} leads to a recursion error")
#         bad_seeds += 1
# print(f"currently {bad_seeds} bad seeds exist")
# with open("output.txt", "w") as file:
#     for row in maze:
#         for cell in row:
#             cell_num = 15
#             if cell.north:
#                 cell_num -= 1
#             if cell.east:
#                 cell_num -= 2
#             if cell.south:
#                 cell_num -= 4
#             if cell.west:
#                 cell_num -= 8
#             file.write(hex(cell_num)[2:].capitalize())
#         file.write("\n")

# gener2 = WilsonsAlgorithm(10, 15, seed=2147483647)
# maze2 = gener2.generate_maze()
# print(maze1 == maze2)
