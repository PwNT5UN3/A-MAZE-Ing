#!/usr/bin/env python3
from typing import Callable, Literal
from src.maze_gen import MazeCell, DFSearch, WilsonsAlgorithm  # noqa 401
from termcolor import colored
from enum import Enum
from src.bfs import BFS
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


def animate_path(
    maze: list[list[MazeCell]],
    renderer: MazeRenderer,
    path: list[tuple[int, int]] | None,
    colorizer: Callable[[str, bool], str] | None = None,
    delay: float = 0.1,
    show_path: bool = True,
    start: tuple[int, int] | None = None,
    end: tuple[int, int] | None = None,
) -> None:
    """Animate the path by drawing it step by step.

    Args:
        maze: The maze grid.
        renderer: MazeRenderer instance.
        path: Full path to animate.
        colorizer: Optional colorizer function.
        delay: Delay in seconds between frames.
        show_path: Whether to animate the path.
        If False, renders once without animation.
    """
    import time
    import os

    if not path or len(path) < 2:
        print("No path to animate")
        return

    # If show_path is False, render once without animation
    if not show_path:
        rendered = renderer.render_maze_walls(
            maze, colorizer, path=None, start=start, end=end
        )
        print(rendered)
        return

    path = path[::-1]

    # Draw maze without path first
    rendered = renderer.render_maze_walls(
        maze, colorizer, path=None, start=start, end=end
    )
    print(rendered)
    time.sleep(delay)

    # Animate path growing step by step
    for i in range(1, len(path) + 1):
        partial_path = path[:i]
        rendered = renderer.render_maze_walls(
            maze, colorizer, path=partial_path, start=start, end=end
        )

        # Clear screen and redraw
        os.system("clear")
        print(rendered)
        time.sleep(delay)


def _select_color_from_list(colors: list[str], prompt: str) -> str | None:
    """Display color selection menu and return chosen color.

    Args:
        colors: List of available color names
        prompt: Prompt to display to user

    Returns:
        Selected color name or None if invalid selection
    """
    import os
    import readchar

    os.system("clear" if os.name != "nt" else "cls")
    print(f"{prompt}\n")
    for idx, c in enumerate(colors, 1):
        print(f"  {idx}. {colored(c, c)}")
    choice = readchar.readchar()
    try:
        return colors[int(choice) - 1]
    except (ValueError, IndexError):
        return None


def color_menu(
    maze: list[list[MazeCell]] | None = None,
    renderer: MazeRenderer | None = None,
    path: list[tuple[int, int]] | None = None,
    show_path: bool = True,
    current_wall_color: str = "yellow",
    current_empty_color: str = "cyan",
    current_path_color: str = "green",
    current_background: str | None = "on_black",
) -> tuple[str, str, str, str | None]:
    """Interactive color selection menu.

    Args:
        maze: Optional maze to render while changing colors
        renderer: Optional MazeRenderer instance
        path: Optional path to display
        show_path: Whether to show the path
        current_wall_color: Current wall color to start with
        current_empty_color: Current empty color to start with
        current_path_color: Current path color to start with
        current_background: Current background color to start with

    Returns:
        Tuple of (wall_color, empty_color, path_color, background_color)
    """
    import os

    def clear_screen() -> None:
        os.system("clear" if os.name != "nt" else "cls")

    try:
        import readchar
    except ImportError:
        print("Error: 'readchar' library not found.")
        return (
            current_wall_color,
            current_empty_color,
            current_path_color,
            current_background,
        )

    # Available colors
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

    wall_color = current_wall_color
    empty_color = current_empty_color
    path_color = current_path_color
    background = current_background

    while True:
        clear_screen()
        print("\n=== Color Configuration Menu ===\n")
        print(f"1 - Wall Color: {wall_color}")
        print(f"2 - Empty Color: {empty_color}")
        print(f"3 - Path Color: {path_color}")
        bg_display = background.replace("on_", "") if background else "None"
        print(f"4 - Background: {bg_display}")
        if maze and renderer:
            print("5 - Preview & Regenerate Maze")
        print("\n0 - Back to Main Menu\n")

        try:
            key = readchar.readchar()

            if key == "1":  # Wall color
                selected = _select_color_from_list(
                    colors, "Select Wall Color:"
                )
                if selected:
                    wall_color = selected

            elif key == "2":  # Empty color
                selected = _select_color_from_list(
                    colors, "Select Empty Space Color:"
                )
                if selected:
                    empty_color = selected

            elif key == "3":  # Path color
                selected = _select_color_from_list(
                    colors, "Select Path Color:"
                )
                if selected:
                    path_color = selected

            elif key == "4":  # Background color
                clear_screen()
                print("Select Background Color:\n")
                print("  1. None (Default)")
                for idx, c in enumerate(background_colors[1:], 2):
                    if c:
                        bg_name = c.replace("on_", "")
                        print(f"  {idx}. {colored(bg_name, 'white', c)}")
                choice = readchar.readchar()
                try:
                    idx = int(choice) - 1
                    background = background_colors[idx]
                except (ValueError, IndexError):
                    pass

            elif key == "5" and maze and renderer:  # Preview maze
                clear_screen()
                current_colorizer = colorize(
                    wall_color=wall_color,
                    fourty_two=empty_color,
                    path_color=path_color,
                    background=background,
                )
                rendered = renderer.render_maze_walls(
                    maze, current_colorizer, path=path if show_path else None
                )
                print(rendered)
                print("\nPress any key to return to color menu...")
                readchar.readchar()

            elif key == "0":
                return wall_color, empty_color, path_color, background

        except KeyboardInterrupt:
            return wall_color, empty_color, path_color, background
        except Exception:
            pass


def _display_maze_with_status(
    maze: list[list[MazeCell]],
    renderer: MazeRenderer,
    colorizer: Callable[[str, bool], str],
    path: list[tuple[int, int]] | None,
    show_path: bool,
) -> None:
    """Render and display maze with status message."""
    import os

    os.system("clear" if os.name != "nt" else "cls")
    rendered = renderer.render_maze_walls(
        maze, colorizer, path=path if (show_path and path) else None
    )
    print(rendered)
    print(
        f"\n[Path: {'VISIBLE' if show_path else 'HIDDEN'}] "
        "Press P to toggle, C for colors, SPACE to regenerate, Q to quit.\n"
    )


def interactive_maze_app(height: int = 14, width: int = 10) -> None:
    """Interactive terminal app for maze generation with path visualization.

    Controls:
        SPACE: Generate maze
        P: Toggle path visibility
        C: Change colors
        Q: Quit
    """

    try:
        import readchar
    except ImportError:
        print("Error: 'readchar' library not found.")
        print("Install it with: pip install readchar")
        return

    def clear_screen() -> None:
        os.system("clear" if os.name != "nt" else "cls")

    gen = WilsonsAlgorithm(height=height, width=width)
    renderer = MazeRenderer()

    wall_color: str = "yellow"
    empty_color: str = "cyan"
    path_color: str = "green"
    background: str | None = "on_black"

    colorizer_func = colorize(
        wall_color=wall_color,
        fourty_two=empty_color,
        path_color=path_color,
        background=background,
    )

    maze = None
    path = None
    show_path_toggle = True

    clear_screen()
    print("╔════════════════════════════════════════════╗")
    print("║         Interactive Maze Generator         ║")
    print("╠════════════════════════════════════════════╣")
    print("║  SPACE - Generate maze                     ║")
    print("║  C     - Change colors                     ║")
    print("║  Q     - Quit                              ║")
    print("╚════════════════════════════════════════════╝")
    print("\nPress SPACE to generate a maze...\n")

    while True:
        try:
            key = readchar.readchar()

            if key.lower() == "q":
                print("\nGoodbye!")
                break

            elif key == " ":
                clear_screen()
                print("Generating maze...\n")
                gen = WilsonsAlgorithm(height=height, width=width)
                maze = gen.generate_maze()

                # Calculate path
                start = (0, 0)
                end = (len(maze) - 1, len(maze[0]) - 1)
                path = BFS().pathfind(maze, start=start, end=end)

                # Animate the path
                if show_path_toggle:
                    animate_path(
                        maze,
                        renderer,
                        path,
                        colorizer=colorizer_func,
                        delay=0.02,
                    )
                else:
                    # Show maze without path animation
                    rendered = renderer.render_maze_walls(
                        maze, colorizer_func, path=None
                    )
                    clear_screen()
                    print(rendered)

                print(
                    f"\n[Path: {'VISIBLE' if show_path_toggle else 'HIDDEN'}] "
                    + "Press P to toggle, C for colors, "
                    + " SPACE to regenerate, Q to quit.\n"
                )

            elif key.lower() == "p":  # P key
                if maze is None:
                    print("Generate a maze first! (Press SPACE)")
                    continue

                show_path_toggle = not show_path_toggle
                _display_maze_with_status(
                    maze, renderer, colorizer_func, path, show_path_toggle
                )

            elif key.lower() == "c":
                new_colors = color_menu(
                    maze=maze,
                    renderer=renderer,
                    path=path,
                    show_path=show_path_toggle,
                    current_wall_color=wall_color,
                    current_empty_color=empty_color,
                    current_path_color=path_color,
                    current_background=background,
                )
                wall_color, empty_color, path_color, background = new_colors
                colorizer_func = colorize(
                    wall_color=wall_color,
                    fourty_two=empty_color,
                    path_color=path_color,
                    background=background,
                )

                if maze is not None:
                    _display_maze_with_status(
                        maze, renderer, colorizer_func, path, show_path_toggle
                    )
                else:
                    clear_screen()
                    print("Colors updated! Press SPACE to generate a maze.\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    interactive_maze_app()
