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

    def render_maze_with_walls(self, maze: list[list[MazeCell]]) -> str:
        """Render maze with proper walls - shows actual wall characters.

        Each cell is rendered as a 3x3 block:
        +--+
        |  |
        +--+

        Open passages remove the wall in that direction.
        """
        if not maze or not maze[0]:
            return ""

        height = len(maze)
        width = len(maze)

        # Each cell needs 3 characters
        # width and 2 lines height (with shared borders)
        lines = []

        # Top border
        line = "┌"
        for c in range(width):
            line += "──"
            if c < width - 1:
                line += "┬"
        line += "┐"
        lines.append(line)

        # Process each row
        for r in range(height):
            # Cell content line (middle of cell)
            line = ""
            for c in range(width):
                cell = maze[r][c]
                # Left wall
                if c == 0:
                    line += "│"
                elif not maze[r][c - 1].east and not cell.west:
                    line += "│"
                else:
                    line += " "

                # Cell interior
                line += "  "

                # Right wall (if last column or wall exists)
                if c == width - 1:
                    line += "│"
            lines.append(line)

            # Bottom border of this row
            if r < height - 1:
                line = ""
                for c in range(width):
                    cell = maze[r][c]
                    cell_below = maze[r + 1][c]

                    # Left corner/junction
                    if c == 0:
                        if not cell.south and not cell_below.north:
                            line += "├"
                        else:
                            line += "│"

                    # Horizontal wall or space
                    if not cell.south and not cell_below.north:
                        line += "──"
                    else:
                        line += "  "

                    # Junction or corner
                    if c < width - 1:
                        cell_right = maze[r][c + 1]
                        cell_below_right = maze[r + 1][c + 1]

                        # Count walls at this junction
                        has_top = not cell.south and not cell_below.north
                        has_bottom = not cell_below.south and not (
                            r + 2 < height and maze[r + 2][c].north
                        )
                        has_left = not cell.east and not cell_right.west
                        has_right = not cell_right.east and not (
                            c + 2 < width and maze[r][c + 2].west
                        )

                        # Choose junction character
                        walls = (has_top, has_right, has_bottom, has_left)
                        junction_map = {
                            (True, True, True, True): "┼",
                            (True, True, True, False): "├",
                            (True, True, False, True): "┴",
                            (True, False, True, True): "┤",
                            (False, True, True, True): "┬",
                            (True, True, False, False): "└",
                            (True, False, True, False): "│",
                            (True, False, False, True): "┘",
                            (False, True, True, False): "┌",
                            (False, True, False, True): "─",
                            (False, False, True, True): "┐",
                            (False, False, False, False): " ",
                        }
                        line += junction_map.get(walls, "┼")
                    else:
                        # Right edge
                        if not cell.south and not cell_below.north:
                            line += "┤"
                        else:
                            line += "│"

                lines.append(line)

        # Bottom border
        line = "└"
        for c in range(width):
            line += "──"
            if c < width - 1:
                line += "┴"
        line += "┘"
        lines.append(line)

        return "\n".join(lines)

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
    gen = WilsonsAlgorithm(height=10, width=9)
    maze = gen.generate_maze()
    parser = MazeParser()

    # Render the maze with proper walls
    rendered = parser.render_maze_with_walls(maze)
    cprint(rendered, "yellow")


if __name__ == "__main__":
    test()
