#!/usr/bin/env python3
from typing import Callable, Literal
from src.maze_gen import MazeCell, DFSearch, WilsonsAlgorithm  # noqa 401
from termcolor import colored
from enum import Enum


def colorize(
    wall_color: str = "yellow",
    fourty_two: str = "cyan",
    background: str | None = None,
) -> Callable[..., str]:
    """Create a colorizer function for maze rendering."""

    def _colorize(text: str, is_wall: bool) -> str:
        color: str = wall_color if is_wall else fourty_two
        return colored(text, color, background)

    return _colorize


class Characters(Enum):
    """Readable enum for wall-connection cases."""

    NONE = ((False, False, False, False), " ")
    NORTH = ((True, False, False, False), "╵")
    SOUTH = ((False, True, False, False), "╷")
    EAST = ((False, False, True, False), "╶")
    WEST = ((False, False, False, True), "╴")

    NORTH_SOUTH = ((True, True, False, False), "│")
    EAST_WEST = ((False, False, True, True), "─")

    NORTH_EAST = ((True, False, True, False), "╰")
    NORTH_WEST = ((True, False, False, True), "╯")
    SOUTH_EAST = ((False, True, True, False), "╭")
    SOUTH_WEST = ((False, True, False, True), "╮")

    NORTH_SOUTH_EAST = ((True, True, True, False), "├")
    NORTH_SOUTH_WEST = ((True, True, False, True), "┤")
    SOUTH_EAST_WEST = ((False, True, True, True), "┬")
    NORTH_EAST_WEST = ((True, False, True, True), "┴")

    NORTH_SOUTH_EAST_WEST = ((True, True, True, True), "┼")

    def __init__(self, tpl: tuple[bool, bool, bool, bool], char: str) -> None:
        self.tuple: tuple[bool, bool, bool, bool] = tpl
        self.char: str = char

    @classmethod
    def from_tuple(cls, tpl: tuple[bool, bool, bool, bool]) -> "Characters":
        """Return the matching Characters member for a (n,s,e,w) tuple."""
        for member in cls:
            if member.tuple == tpl:
                return member
        return cls.NONE


class MazeRenderer:
    def __init__(self) -> None:
        self.char_map: dict[tuple[bool, bool, bool, bool], str] = {
            member.tuple: member.char for member in Characters
        }

    def get_wall_char(self, n: bool, s: bool, e: bool, w: bool) -> str:
        return Characters.from_tuple((n, s, e, w)).char

    def render_maze_walls(
        self,
        maze: list[list[MazeCell]],
        colorizer: Callable[[str, bool, int, int], str] | None,
    ) -> str:
        rows: int = len(maze)
        cols: int = len(maze[0])

        is_wall, content_grid, grid_h, grid_w = self._init_grids(rows, cols)
        self._carve_passages(maze, is_wall, content_grid, rows, cols)
        self._apply_forty_two_pattern(maze, content_grid, rows, cols)

        return self._render_lines(
            is_wall, content_grid, grid_h, grid_w, colorizer
        )

    def _init_grids(
        self, rows: int, cols: int
    ) -> tuple[list[list[bool]], list[list[str]], int, int]:
        grid_h: int = rows * 2 + 1
        grid_w: int = cols * 2 + 1

        is_wall: list[list[bool]] = [
            [True for _ in range(grid_w)] for _ in range(grid_h)
        ]
        content_grid: list[list[str]] = [
            ["  " for _ in range(grid_w)] for _ in range(grid_h)
        ]

        return is_wall, content_grid, grid_h, grid_w

    def _carve_passages(
        self,
        maze: list[list[MazeCell]],
        is_wall: list[list[bool]],
        content_grid: list[list[str]],
        rows: int,
        cols: int,
    ) -> None:
        for r in range(rows):
            for c in range(cols):
                cell: MazeCell = maze[r][c]
                center_r, center_c = r * 2 + 1, c * 2 + 1

                is_wall[center_r][center_c] = False

                if cell.east:
                    is_wall[center_r][center_c + 1] = False
                if cell.south:
                    is_wall[center_r + 1][center_c] = False

                # initialize any special content cell with blanks for now
                content_grid[center_r][center_c] = content_grid[center_r][
                    center_c
                ]

    def _apply_forty_two_pattern(
        self,
        maze: list[list[MazeCell]],
        content_grid: list[list[str]],
        rows: int,
        cols: int,
    ) -> None:
        for r in range(rows):
            for c in range(cols):
                cell: MazeCell = maze[r][c]
                if not cell.fourty_two_pattern:
                    continue

                center_r, center_c = r * 2 + 1, c * 2 + 1
                content_grid[center_r][center_c] = "▓▓"

    def _render_lines(
        self,
        is_wall: list[list[bool]],
        content_grid: list[list[str]],
        grid_h: int,
        grid_w: int,
        colorizer: Callable[[str, bool, int, int], str] | None,
    ) -> str:
        lines: list[str] = []
        for r in range(grid_h):
            line_chars: list[str] = []
            for c in range(grid_w):
                if is_wall[r][c]:
                    n: bool = r > 0 and is_wall[r - 1][c]
                    s: bool = r < grid_h - 1 and is_wall[r + 1][c]
                    w: bool = c > 0 and is_wall[r][c - 1]
                    e: bool = c < grid_w - 1 and is_wall[r][c + 1]

                    base_char = self.get_wall_char(n, s, e, w)
                    padding: Literal["─", " "] = "─" if e else " "
                    rendered = base_char + padding

                    if colorizer:
                        rendered = colorizer(rendered, True)

                    line_chars.append(rendered)
                else:
                    rendered = content_grid[r][c]
                    if colorizer:
                        rendered = colorizer(rendered, False)
                    line_chars.append(rendered)
            lines.append("".join(line_chars))

        return "\n".join(lines)


def test() -> None:
    gen = DFSearch(height=14, width=10)
    maze = gen.generate_maze()
    parser = MazeRenderer()

    rendered = parser.render_maze_walls(
        maze,
        colorizer=colorize(
            wall_color="yellow",
            fourty_two="cyan",
            background="on_black",
        ),
    )
    print(rendered)

    # # Optional: show raw coordinates
    # coordinates = parser.get_raw_coordinates(maze)
    # print(f"\nTotal cells: {len(coordinates)}")


if __name__ == "__main__":
    test()
