#!/usr/bin/env python3
from turtle import width
from typing import Callable, Literal, Type
import bfs
from src.maze_gen import (
    MazeCell,
    DFSearch,
    WilsonsAlgorithm,
    MazeGenerator,  # noqa 401
)
from termcolor import colored
from enum import Enum
from src.bfs import BFS, Finding
import os


def colorize(
    wall_color: str = "yellow",
    fourty_two: str = "cyan",
    path_color: str | None = None,
    background: str | None = None,
    start_color: str = "red",
    end_color: str = "magenta",
    start_marker: str = "S",
    end_marker: str = "E",
) -> Callable[..., str]:
    """Create a colorizer function for maze rendering.

    Args:
        wall_color: Color for walls.
        fourty_two: Color for the 42 pattern cells.
        path_color: Color for path markers (• and connectors).
        If None, uses fourty_two color.
        background: Background color.
        start_color: Color for the start marker.
        end_color: Color for the end marker.
        start_marker: Character used for the start marker (before padding).
        end_marker: Character used for the end marker (before padding).
    """

    def _colorize(text: str, is_wall: bool) -> str:
        stripped = text.strip()

        if path_color and stripped == "░░":
            return colored(text, path_color, background)

        if stripped == start_marker:
            return colored(text, start_color, background)

        if stripped == end_marker:
            return colored(text, end_color, background)

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
        colorizer: Callable[[str, bool], str] | None,
        path: list[tuple[int, int]] | None = None,
        start: tuple[int, int] | None = None,
        end: tuple[int, int] | None = None,
    ) -> str:
        rows: int = len(maze)
        cols: int = len(maze[0])

        is_wall, content_grid, grid_h, grid_w = self._init_grids(rows, cols)
        self._carve_passages(maze, is_wall, content_grid, rows, cols)
        self._apply_forty_two_pattern(maze, content_grid, rows, cols)
        self._apply_solved_path(content_grid, path)
        self._mark_endpoints(content_grid, rows, cols, start=start, end=end)

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

    def _apply_solved_path(
        self,
        content_grid: list[list[str]],
        path: list[tuple[int, int]] | None,
        marker: str = "░░",
    ) -> None:
        if not path:
            return
        self._mark_path_nodes(content_grid, path, marker)
        self._add_path_connectors(content_grid, path)

    def _mark_path_nodes(
        self,
        content_grid: list[list[str]],
        path: list[tuple[int, int]],
        marker: str,
    ) -> None:
        """Mark path nodes on the content grid."""
        for r, c in path:
            cr, cc = r * 2 + 1, c * 2 + 1
            content_grid[cr][cc] = marker

    def _add_path_connectors(
        self, content_grid: list[list[str]], path: list[tuple[int, int]]
    ) -> None:
        """Connect consecutive nodes with segments along corridors."""
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            cr1, cc1 = r1 * 2 + 1, c1 * 2 + 1
            # Horizontal step
            if r1 == r2 and c2 == c1 + 1:
                # east corridor between centers
                content_grid[cr1][cc1 + 1] = "░░"
            elif r1 == r2 and c2 == c1 - 1:
                # west corridor between centers
                content_grid[cr1][cc1 - 1] = "░░"
            # Vertical step
            elif c1 == c2 and r2 == r1 + 1:
                # south corridor between centers
                content_grid[cr1 + 1][cc1] = "░░"
            elif c1 == c2 and r2 == r1 - 1:
                # north corridor between centers
                content_grid[cr1 - 1][cc1] = "░░"

    def _mark_endpoints(
        self,
        content_grid: list[list[str]],
        rows: int,
        cols: int,
        *,
        start: tuple[int, int] | None,
        end: tuple[int, int] | None,
        start_marker: str = "S ",
        end_marker: str = "E ",
    ) -> None:
        start_coord = start if start is not None else (0, 0)
        end_coord = end if end is not None else (rows - 1, cols - 1)

        sr, sc = start_coord
        er, ec = end_coord

        content_grid[sr * 2 + 1][sc * 2 + 1] = start_marker
        content_grid[er * 2 + 1][ec * 2 + 1] = end_marker

    def _render_lines(
        self,
        is_wall: list[list[bool]],
        content_grid: list[list[str]],
        grid_h: int,
        grid_w: int,
        colorizer: Callable[[str, bool], str] | None,
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


class Terminal:
    """Interactive terminal driver with configurable algorithms and sizing."""

    def __init__(
        self,
        *,
        maze_generator_cls: Type[MazeGenerator] = WilsonsAlgorithm,
        pathfinder_cls: Type[Finding] = BFS,
        width: int = 10,
        height: int = 14,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
        delay: float = 0.02,
    ) -> None:
        self.maze_generator_cls = maze_generator_cls
        self.pathfinder_cls = pathfinder_cls
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit if exit is not None else (height - 1, width - 1)
        self.delay = delay

        self.renderer = MazeRenderer()
        self.wall_color: str = "yellow"
        self.empty_color: str = "cyan"
        self.path_color: str = "green"
        self.background: str | None = "on_black"
        self.colorizer = self._build_colorizer()

        self.maze: list[list[MazeCell]] | None = None
        self.path: list[tuple[int, int]] | None = None
        self.show_path: bool = True

    @staticmethod
    def _clear_screen() -> None:
        os.system("clear" if os.name != "nt" else "cls")

    def _build_colorizer(self) -> Callable[[str, bool], str]:
        return colorize(
            wall_color=self.wall_color,
            fourty_two=self.empty_color,
            path_color=self.path_color,
            background=self.background,
        )

    def _select_color_from_list(
        self, colors: list[str], prompt: str
    ) -> str | None:
        import readchar

        self._clear_screen()
        print(f"{prompt}\n")
        for idx, color_name in enumerate(colors, 1):
            print(f"  {idx}. {colored(color_name, color_name)}")
        choice = readchar.readchar()
        try:
            return colors[int(choice) - 1]
        except (ValueError, IndexError):
            return None

    def _color_menu(self) -> None:
        try:
            import readchar
        except ImportError:
            print(
                "Error: 'readchar' library not found. Install it with: pip install readchar"
            )
            return

        colors = [
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "grey",
        ]
        background_colors = [
            None,
            "on_red",
            "on_green",
            "on_yellow",
            "on_blue",
            "on_magenta",
            "on_cyan",
            "on_white",
        ]

        while True:
            self._clear_screen()
            print("\n=== Color Configuration Menu ===\n")
            print(f"1 - Wall Color: {self.wall_color}")
            print(f"2 - Empty Color: {self.empty_color}")
            print(f"3 - Path Color: {self.path_color}")
            bg_display = (
                self.background.replace("on_", "")
                if self.background
                else "None"
            )
            print(f"4 - Background: {bg_display}")
            if self.maze and self.renderer:
                print("5 - Preview & Regenerate Maze")
            print("\n0 - Back to Main Menu\n")

            try:
                key = readchar.readchar()

                if key == "1":
                    selected = self._select_color_from_list(
                        colors, "Select Wall Color:"
                    )
                    if selected:
                        self.wall_color = selected

                elif key == "2":
                    selected = self._select_color_from_list(
                        colors, "Select Empty Space Color:"
                    )
                    if selected:
                        self.empty_color = selected

                elif key == "3":
                    selected = self._select_color_from_list(
                        colors, "Select Path Color:"
                    )
                    if selected:
                        self.path_color = selected

                elif key == "4":
                    self._clear_screen()
                    print("Select Background Color:\n")
                    print("  1. None (Default)")
                    for idx, bg in enumerate(background_colors[1:], 2):
                        if bg:
                            bg_name = bg.replace("on_", "")
                            print(f"  {idx}. {colored(bg_name, 'white', bg)}")
                    choice = readchar.readchar()
                    try:
                        idx = int(choice) - 1
                        self.background = background_colors[idx]
                    except (ValueError, IndexError):
                        pass

                elif key == "5" and self.maze:
                    self.colorizer = self._build_colorizer()
                    self._render_current_maze(force_show_path=True)
                    print("\nPress any key to return to color menu...")
                    readchar.readchar()

                elif key == "0":
                    self.colorizer = self._build_colorizer()
                    return

            except KeyboardInterrupt:
                self.colorizer = self._build_colorizer()
                return

    def _render_current_maze(
        self, force_show_path: bool | None = None
    ) -> None:
        if self.maze is None:
            print("No maze generated yet. Press SPACE to generate one.")
            return

        show_path = (
            self.show_path if force_show_path is None else force_show_path
        )
        rendered = self.renderer.render_maze_walls(
            self.maze,
            self.colorizer,
            path=self.path if (show_path and self.path) else None,
            start=self.entry,
            end=self.exit,
        )
        self._clear_screen()
        print(rendered)
        print(
            f"\n[Path: {'VISIBLE' if show_path else 'HIDDEN'}] "
            "Press P to toggle, C for colors, SPACE to regenerate, Q to quit.\n"
        )

    def _animate_path(self) -> None:
        import time

        if not self.maze or not self.path or len(self.path) < 2:
            print("No path to animate")
            return

        path_steps = self.path[::-1]

        rendered = self.renderer.render_maze_walls(
            self.maze,
            self.colorizer,
            path=None,
            start=self.entry,
            end=self.exit,
        )
        print(rendered)
        time.sleep(self.delay)

        for i in range(1, len(path_steps) + 1):
            partial_path = path_steps[:i]
            rendered = self.renderer.render_maze_walls(
                self.maze,
                self.colorizer,
                path=partial_path,
                start=self.entry,
                end=self.exit,
            )
            self._clear_screen()
            print(rendered)
            time.sleep(self.delay)

    def _generate_maze_and_path(self) -> None:
        generator = self.maze_generator_cls(
            width=self.width, height=self.height
        )
        self.maze = generator.generate_maze()

        solver = self.pathfinder_cls()
        self.path = solver.pathfind(
            self.maze,
            start=self.entry,
            end=self.exit,
        )

    def run(self) -> None:
        try:
            import readchar
        except ImportError:
            print(
                "Error: 'readchar' library not found. Install it with: pip install readchar"
            )
            return

        self._clear_screen()
        print("╔════════════════════════════════════════════╗")
        print("║         Interactive Maze Generator         ║")
        print("╠════════════════════════════════════════════╣")
        print("║  SPACE - Generate maze                     ║")
        print("║  P     - Toggle path visibility            ║")
        print("║  C     - Change colors                     ║")
        print("║  Q     - Quit                              ║")
        print("╚════════════════════════════════════════════╝")
        print(
            f"\nWidth={self.width}, Height={self.height}, Entry={self.entry}, Exit={self.exit}\n"
            "Press SPACE to generate a maze...\n"
        )

        while True:
            try:
                key = readchar.readchar()

                if key.lower() == "q":
                    print("\nGoodbye!")
                    break

                if key == " ":
                    self._clear_screen()
                    print("Generating maze...\n")
                    self._generate_maze_and_path()

                    if self.show_path and self.path:
                        self._animate_path()
                    else:
                        self._render_current_maze(force_show_path=False)

                elif key.lower() == "p":
                    if self.maze is None:
                        print("Generate a maze first! (Press SPACE)")
                        continue
                    self.show_path = not self.show_path
                    self._render_current_maze()

                elif key.lower() == "c":
                    self._color_menu()
                    if self.maze:
                        self._render_current_maze()
                    else:
                        self._clear_screen()
                        print(
                            "Colors updated! Press SPACE to generate a maze.\n"
                        )

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as exc:  # pragma: no cover - user I/O guard
                print(f"Error: {exc}")
                break


class MazeAppManager:
    """Simple coordinator to wire algorithms, sizing, and the terminal UI."""

    def __init__(
        self,
        *,
        maze_generator_cls: Type[MazeGenerator] = WilsonsAlgorithm,
        pathfinder_cls: Type[Finding] = BFS,
        width: int = 10,
        height: int = 14,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
        delay: float = 0.02,
    ) -> None:
        self.terminal = Terminal(
            maze_generator_cls=maze_generator_cls,
            pathfinder_cls=pathfinder_cls,
            width=width,
            height=height,
            entry=entry,
            exit=exit,
            delay=delay,
        )

    def run(self) -> None:
        self.terminal.run()


def interactive_maze_app(
    height: int = 14,
    width: int = 10,
    entry: tuple[int, int] = (0, 0),
    exit: tuple[int, int] | None = None,
    maze_generator_cls: Type[MazeGenerator] = WilsonsAlgorithm,
    pathfinder_cls: Type[Finding] = BFS,
) -> None:
    """Backward-compatible wrapper that launches the terminal UI."""

    manager: MazeAppManager = MazeAppManager(
        maze_generator_cls=maze_generator_cls,
        pathfinder_cls=pathfinder_cls,
        width=width,
        height=height,
        entry=entry,
        exit=exit,
    )
    manager.run()


if __name__ == "__main__":
    # Simple manual test entry point
    interactive_maze_app(
        height=30,
        width=20,
        entry=(0, 0),
        exit=(20, 19),
        maze_generator_cls=DFSearch,
        pathfinder_cls=BFS,
    )
