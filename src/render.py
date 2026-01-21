from src.maze_gen import MazeCell, DFSearch, WilsonsAlgorithm
from termcolor import colored, cprint
from pprint import pprint


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
            tuple[bool](atr.north, atr.east, atr.south, atr.west)
            for cell in maze
            for atr in cell
        ]

    def get_char_for_border(
        self,
        north: bool,
        south: bool,
        east: bool,
        west: bool,
        fourty_two_pattern: bool,
    ) -> str:
        """Map open passage directions to appropriate Unicode box-drawing
        character.

        Args:
            north, south, east, west: True if passage is open in that direction
            (matching MazeCell field order)

        Returns:
            Unicode box-drawing character representing the cell
        """
        #   N
        # W   E
        #   S
        # Lookup table: (N, S, E, W)
        char_map = {
            # --- 1. NO CONNECTIONS (Isolated) ---
            # Was "cross", should be empty or a small dot/pillar
            (False, False, False, False): " ",
            # --- 2. SINGLE CONNECTIONS (Dead Ends) ---
            (True, False, False, False): "╵",  # North only (Stub Up)
            (False, True, False, False): "╷",  # South only (Stub Down)
            (False, False, True, False): "╶",  # East only (Stub Right)
            (False, False, False, True): "╴",  # West only (Stub Left)
            # --- 3. TWO CONNECTIONS (Straight) ---
            (True, True, False, False): "│",  # N + S (Vertical Wall)
            (False, False, True, True): "─",  # E + W (Horizontal Wall)
            # --- 4. TWO CONNECTIONS (Corners) ---
            (True, False, True, False): "╰",  # N + E (Bottom-Left Corner)
            (True, False, False, True): "╯",  # N + W (Bottom-Right Corner)
            (False, True, True, False): "╭",  # S + E (Top-Left Corner)
            (False, True, False, True): "╮",  # S + W (Top-Right Corner)
            # --- 5. THREE CONNECTIONS (T-Junctions) ---
            (True, True, True, False): "├",  # N+S+E (Vertical + Right)
            (True, True, False, True): "┤",  # N+S+W (Vertical + Left)
            (False, True, True, True): "┬",  # S+E+W (Horizontal + Down)
            (True, False, True, True): "┴",  # N+E+W (Horizontal + Up)
            # --- 6. ALL CONNECTIONS (Cross) ---
            (True, True, True, True): "┼",  # N+S+E+W
        }
        if fourty_two_pattern:
            return MAZE_ROUNDED["FLAG_SPECIAL_DOT"]
        return char_map.get((north, south, east, west), MAZE_ROUNDED["empty"])

    def render_maze_to_string(
        self,
        maze: list[list[MazeCell]],
    ) -> str:
        lines = []
        for row in maze:
            line = ""
            for cell in row:
                char = self.get_char_for_border(
                    north=cell.north,
                    south=cell.south,
                    east=cell.east,
                    west=cell.west,
                    fourty_two_pattern=cell.fourty_two_pattern,
                )
                line += char
            lines.append(line)
        return "\n".join(lines)


def test() -> None:
    gen = DFSearch(height=70, width=40)
    maze = gen.generate_maze()
    parser = MazeParser()

    # Render the maze with Unicode characters
    rendered = parser.render_maze_to_string(maze)
    print(rendered)

    # # Optional: show raw coordinates
    # coordinates = parser.get_raw_coordinates(maze)
    # print(f"\nTotal cells: {len(coordinates)}")


if __name__ == "__main__":
    test()
