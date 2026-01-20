from ast import Tuple
import pprint
from turtle import width
from maze_generator.maze_gen import MazeCell, DFSearch, WilsonsAlgorithm
from termcolor import colored, cprint
from pprint import pprint

MAZE_ROUNDED = {
    "wall_v": "│",
    "wall_h": "─",
    "corn_tl": "╭",
    "corn_tr": "╮",
    "corn_bl": "╰",
    "corn_br": "╯",
    "t_down": "┬",
    "t_up": "┴",
    "t_right": "├",
    "t_left": "┤",
    "cross": "┼",
    "empty": " ",
}


class MazeParser:

    # north: bool
    # south: bool
    # east: bool
    # west: bool
    #   N
    # W    E
    #   S
    def get_raw_coordinates(
        self,
        maze: list[list[MazeCell]],
    ) -> list[tuple[int, int]]:
        return [tuple(atr.coordinates) for cell in maze for atr in cell]

    def get_raw_directions(
        self,
        maze: list[list[MazeCell]],
    ) -> list[tuple[bool]]:
        return [
            tuple(atr.north, atr.east, atr.south, atr.west)
            for cell in maze
            for atr in cell
        ]

    def get_char_for_border(
        self, north: bool, east: bool, south: bool, west: bool
    ) -> str:
        """Map open passage directions to appropriate Unicode box-drawing
        character.

        Args:
            north, east, south, west: True if passage is open in that direction

        Returns:
            Unicode box-drawing character representing the cell
        """
        # Lookup table: (N, E, S, W) -> character
        char_map = {
            # No passages open (all walls) - cross
            (False, False, False, False): MAZE_ROUNDED["cross"],
            # Single passage open
            (True, False, False, False): MAZE_ROUNDED[
                "wall_v"
            ],  # │ north only
            (False, True, False, False): MAZE_ROUNDED["wall_h"],  # ─ east only
            (False, False, True, False): MAZE_ROUNDED[
                "wall_v"
            ],  # │ south only
            (False, False, False, True): MAZE_ROUNDED["wall_h"],  # ─ west only
            # Two passages open - corners
            (True, True, False, False): MAZE_ROUNDED[
                "corn_bl"
            ],  # ╰ north + east
            (True, False, False, True): MAZE_ROUNDED[
                "corn_br"
            ],  # ╯ north + west
            (False, True, True, False): MAZE_ROUNDED[
                "corn_tl"
            ],  # ╭ east + south
            (False, False, True, True): MAZE_ROUNDED[
                "corn_tr"
            ],  # ╮ south + west
            # Two passages open - straight through
            (True, False, True, False): MAZE_ROUNDED[
                "wall_v"
            ],  # │ north + south
            (False, True, False, True): MAZE_ROUNDED[
                "wall_h"
            ],  # ─ east + west
            # Three passages open - T-junctions
            (True, True, True, False): MAZE_ROUNDED[
                "t_left"
            ],  # ┤ N+E+S (no west)
            (True, True, False, True): MAZE_ROUNDED[
                "t_down"
            ],  # ┬ N+E+W (no south)
            (True, False, True, True): MAZE_ROUNDED[
                "t_right"
            ],  # ├ N+S+W (no east)
            (False, True, True, True): MAZE_ROUNDED[
                "t_up"
            ],  # ┴ E+S+W (no north)
            # All passages open
            (True, True, True, True): MAZE_ROUNDED["empty"],  # ┼ all open
        }

        return char_map.get((north, east, south, west), MAZE_ROUNDED["empty"])

    def render_maze_to_string(
        self, maze: list[list[MazeCell]], cell_size: int = 1
    ) -> str:
        """Render the maze as a string with Unicode box-drawing characters.

        Args:
            maze: 2D list of MazeCell objects
            cell_size: Size multiplier for each cell
            (1=normal, 2=double, 3=triple, etc.)

        Returns:
            String representation of the maze
        """
        if cell_size == 1:
            # Original compact rendering
            lines = []
            for row in maze:
                line = ""
                for cell in row:
                    char = self.get_char_for_border(
                        north=cell.north,
                        east=cell.east,
                        south=cell.south,
                        west=cell.west,
                    )
                    line += char
                lines.append(line)
            return "\n".join(lines)
        else:
            # Larger rendering with walls and spaces
            lines = []
            for row in maze:
                # Create multiple lines per row
                for line_offset in range(cell_size):
                    line = ""
                    for cell in row:
                        if line_offset == 0:
                            # Top edge
                            if cell.north:
                                line += " " * cell_size
                            else:
                                line += "─" * cell_size
                        elif line_offset == cell_size - 1:
                            # Bottom edge
                            if cell.south:
                                line += " " * cell_size
                            else:
                                line += "─" * cell_size
                        else:
                            # Middle lines
                            if cell.west:
                                line += " "
                            else:
                                line += "│"
                            line += " " * (cell_size - 2)
                            if cell.east:
                                line += " "
                            else:
                                line += "│"
                    lines.append(line)
            return "\n".join(lines)


def test() -> None:
    gen = WilsonsAlgorithm(height=70, width=40)
    maze = gen.generate_maze()
    parser = MazeParser()

    # Render the maze with Unicode characters
    rendered = parser.render_maze_to_string(maze)
    pprint(rendered)

    # # Optional: show raw coordinates
    # coordinates = parser.get_raw_coordinates(maze)
    # print(f"\nTotal cells: {len(coordinates)}")


if __name__ == "__main__":
    test()
