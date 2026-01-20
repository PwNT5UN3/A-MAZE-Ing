from mazegen import DFSearch, WilsonsAlgorithm


print("generating...")
gen = WilsonsAlgorithm(50, 50)
maze = gen.generate_maze()
# gen2 = DFSearch(50, 50)
# maze2 = gen2.generate_maze()
# check_perfection(gen, maze)
# check_perfection(gen2, maze2)
with open("output.txt", "w") as file:
    for row in maze:
        for cell in row:
            open_walls = 0
            cell_num = 15
            if cell.north:
                cell_num -= 1
                open_walls += 1
            if cell.east:
                cell_num -= 2
                open_walls += 1
            if cell.south:
                cell_num -= 4
                open_walls += 1
            if cell.west:
                cell_num -= 8
                open_walls += 1
            file.write(hex(cell_num)[2:].capitalize())
        file.write("\n")
