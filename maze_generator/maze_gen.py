from numpy import random as nprand
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class MazeCell:
    north: bool
    south: bool
    east: bool
    west: bool
    fourty_two_pattern: bool
    coordinates: Tuple[int, ...]


class MazeGenerator(ABC):
    """The core maze generator"""

    def __init__(
        self, height: int, width: int, *, seed: int | None = None
    ) -> None:
        if seed is None:
            seed = nprand.randint(0, high=2147483647)
        self.rng = nprand.Generator(nprand.MT19937(seed=seed))
        self.width = width
        self.height = height
        if self.check_42_pattern_avilability():
            self.pattern_coordinates = self.get_pattern_coords()
        else:
            self.pattern_coordinates = []
        self.maze = self.create_maze_canvas()

    def check_42_pattern_avilability(self) -> bool:
        if self.width >= 14:
            if self.height >= 10:
                return True
        return False

    def get_pattern_coords(self) -> List[tuple]:
        coordinates = []
        upper_left = tuple(
            [int((self.height - 5) / 2), int((self.width - 7) / 2)]
        )
        coordinates.append(upper_left)
        coordinates.append(tuple([upper_left[0] + 1, upper_left[1]]))
        coordinates.append(tuple([upper_left[0] + 2, upper_left[1]]))
        coordinates.append(tuple([upper_left[0] + 2, upper_left[1] + 1]))
        coordinates.append(tuple([upper_left[0] + 2, upper_left[1] + 2]))
        coordinates.append(tuple([upper_left[0] + 3, upper_left[1] + 2]))
        coordinates.append(tuple([upper_left[0] + 4, upper_left[1] + 2]))
        coordinates.append(tuple([upper_left[0], upper_left[1] + 4]))
        coordinates.append(tuple([upper_left[0] + 2, upper_left[1] + 4]))
        coordinates.append(tuple([upper_left[0] + 3, upper_left[1] + 4]))
        coordinates.append(tuple([upper_left[0] + 4, upper_left[1] + 4]))
        coordinates.append(tuple([upper_left[0], upper_left[1] + 5]))
        coordinates.append(tuple([upper_left[0] + 2, upper_left[1] + 5]))
        coordinates.append(tuple([upper_left[0] + 4, upper_left[1] + 5]))
        coordinates.append(tuple([upper_left[0], upper_left[1] + 6]))
        coordinates.append(tuple([upper_left[0] + 1, upper_left[1] + 6]))
        coordinates.append(tuple([upper_left[0] + 2, upper_left[1] + 6]))
        coordinates.append(tuple([upper_left[0] + 4, upper_left[1] + 6]))
        return coordinates

    def create_maze_canvas(self) -> List[List[MazeCell]]:
        canvas = []
        for lane in range(self.height):
            row = []
            for cell in range(self.width):
                if tuple([lane, cell]) in self.pattern_coordinates:
                    row.append(
                        MazeCell(
                            False,
                            False,
                            False,
                            False,
                            True,
                            tuple([lane, cell]),
                        )
                    )
                else:
                    row.append(
                        MazeCell(
                            False,
                            False,
                            False,
                            False,
                            False,
                            tuple([lane, cell]),
                        )
                    )
            canvas.append(row)
        self._cell_map = {c.coordinates: c for r in canvas for c in r}
        return canvas

    def get_all_coords(self) -> List[tuple]:
        coords = []
        for row in self.maze:
            for cell in row:
                coords.append(cell.coordinates)
        return coords

    def remove_cell_from_array(self, cell: tuple, array: List[List]) -> None:
        for row in array:
            for canvas_cell in row:
                if canvas_cell.coordinates == cell:
                    row.remove(canvas_cell)

    def get_maze_cell_from_coordinate(self, coordinate: tuple) -> MazeCell:
        # for row in self.maze:
        #     for cell in row:
        #         if cell.coordinates == coordinate:
        #             return cell
        # raise ValueError("Unexpected Error")
        try:
            return self._cell_map[coordinate]
        except KeyError:
            raise ValueError("Unexpected Error")

    def get_available_cells(
        self, current_cell: MazeCell, available: list
    ) -> Dict[str, MazeCell]:
        cells = {}
        north = (current_cell.coordinates[0] - 1, current_cell.coordinates[1])
        south = (current_cell.coordinates[0] + 1, current_cell.coordinates[1])
        east = (current_cell.coordinates[0], current_cell.coordinates[1] + 1)
        west = (current_cell.coordinates[0], current_cell.coordinates[1] - 1)
        if north in available:
            cells["north"] = self.get_maze_cell_from_coordinate(north)
        if south in available:
            cells["south"] = self.get_maze_cell_from_coordinate(south)
        if east in available:
            cells["east"] = self.get_maze_cell_from_coordinate(east)
        if west in available:
            cells["west"] = self.get_maze_cell_from_coordinate(west)
        return cells

    @abstractmethod
    def generate_maze(self) -> List[List[MazeCell]]:
        pass


class WilsonsAlgorithm(MazeGenerator):
    def __init__(
        self, width: int, height: int, *, seed: int | None = None
    ) -> None:
        super().__init__(width, height, seed=seed)

    def generate_maze(self) -> List[List[MazeCell]]:
        maze = self.maze
        available = self.get_all_coords()
        for pattern_cell in self.pattern_coordinates:
            available.remove(pattern_cell)
        unvisited = available.copy()
        existing_maze = set()
        first_maze_cell_np = tuple(self.rng.choice(available))
        existing_maze.add(
            tuple([int(first_maze_cell_np[0]), int(first_maze_cell_np[1])])
        )
        unvisited.remove(
            tuple([int(first_maze_cell_np[0]), int(first_maze_cell_np[1])])
        )
        move_stack: list = []

        def random_looperased_walk(current_cell: MazeCell) -> None:
            if current_cell.coordinates in move_stack:
                while current_cell in move_stack:
                    move_stack.pop()
            if current_cell.coordinates in existing_maze:
                for cell in move_stack:
                    existing_maze.add(cell)
                    if cell in unvisited:
                        unvisited.remove(cell)
                move_stack.clear()
                return
            move_stack.append(current_cell.coordinates)
            if len(move_stack) == 100:
                move_stack.clear()
                return
            adjacent = self.get_available_cells(
                current_cell, available=available
            )
            previous = None
            for directions in adjacent.keys():
                if (
                    adjacent[directions].coordinates
                    == move_stack[len(move_stack) - 2]
                ):
                    previous = directions
            if previous is not None:
                adjacent.pop(previous)
            if adjacent == {}:
                for cell in move_stack:
                    existing_maze.add(cell)
                    if cell in unvisited:
                        unvisited.remove(cell)
                move_stack.clear()
                return
            choice = self.rng.choice(list(adjacent.keys()))
            if choice == "north":
                current_cell.north = True
                adjacent["north"].south = True
                return random_looperased_walk(adjacent["north"])
            elif choice == "south":
                current_cell.south = True
                adjacent["south"].north = True
                return random_looperased_walk(adjacent["south"])
            elif choice == "east":
                current_cell.east = True
                adjacent["east"].west = True
                return random_looperased_walk(adjacent["east"])
            elif choice == "west":
                current_cell.west = True
                adjacent["west"].east = True
                return random_looperased_walk(adjacent["west"])

        while len(unvisited) != 0:
            walk_start_np = tuple(self.rng.choice(unvisited))
            walk_start = tuple([int(walk_start_np[0]), int(walk_start_np[1])])
            random_looperased_walk(
                self.get_maze_cell_from_coordinate(walk_start)
            )
        return maze


class DFSearch(MazeGenerator):
    def __init__(
        self, width: int, height: int, *, seed: int | None = None
    ) -> None:
        super().__init__(width, height, seed=seed)

    def generate_maze(self) -> List[List[MazeCell]]:
        maze = self.maze
        available = self.get_all_coords()
        for pattern_cell in self.pattern_coordinates:
            available.remove(pattern_cell)
        start_np = tuple(self.rng.choice(available))
        start = tuple([int(start_np[0]), int(start_np[1])])
        available.remove(start)
        move_stack = []
        move_stack.append(start)

        def random_walk(current: MazeCell) -> None:
            adjacent = self.get_available_cells(current, available=available)
            if len(available) == 0:
                return
            if adjacent == {}:
                move_stack.pop()
                return random_walk(
                    self.get_maze_cell_from_coordinate(
                        move_stack[len(move_stack) - 1]
                    )
                )
            choice = self.rng.choice(list(adjacent.keys()))
            if choice == "north":
                current.north = True
                adjacent["north"].south = True
                available.remove(adjacent["north"].coordinates)
                move_stack.append(adjacent["north"].coordinates)
                return random_walk(adjacent["north"])
            elif choice == "south":
                current.south = True
                adjacent["south"].north = True
                available.remove(adjacent["south"].coordinates)
                move_stack.append(adjacent["south"].coordinates)
                return random_walk(adjacent["south"])
            elif choice == "east":
                current.east = True
                adjacent["east"].west = True
                available.remove(adjacent["east"].coordinates)
                move_stack.append(adjacent["east"].coordinates)
                return random_walk(adjacent["east"])
            elif choice == "west":
                current.west = True
                adjacent["west"].east = True
                available.remove(adjacent["west"].coordinates)
                move_stack.append(adjacent["west"].coordinates)
                return random_walk(adjacent["west"])

        random_walk(self.get_maze_cell_from_coordinate(start))
        return maze
