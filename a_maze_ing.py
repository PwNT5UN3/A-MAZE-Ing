from maze_generator import WilsonsAlgorithm

gen = WilsonsAlgorithm(10, 15)
maze = gen.generate_maze()
with open('output.txt', 'w') as file:
    for row in maze:
        for cell in row:
            cell_num = 15
            if cell.north:
                cell_num -= 1
            if cell.east:
                cell_num -= 2
            if cell.south:
                cell_num -= 4
            if cell.west:
                cell_num -= 8
            file.write(hex(cell_num)[2:].capitalize())
        file.write('\n')
