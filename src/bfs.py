#!/usr/bin/env python3
from collections import deque
from typing import Protocol, runtime_checkable
from src.maze_gen import DFSearch, MazeCell, MazeGenerator


@runtime_checkable
class Finding(Protocol):

    def pathfind(
        self,
        maze: list[list[MazeCell]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        pass

    def path_to_directions(self, path: list[tuple[int, int]]) -> list[str]: ...


class BFS:
    """Time complexity: O(V + E), where V is the number of cells and E
    is the number of connections between cells
    """

    def pathfind(
        self,
        maze: list[list[MazeCell]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        height: int = len(maze)
        width: int = len(maze[0]) if height > 0 else 0

        if not (0 <= start[0] < height and 0 <= start[1] < width):
            return None
        if not (0 <= end[0] < height and 0 <= end[1] < width):
            return None

        queue = deque([start])
        parent = {start: None}

        while queue:
            current = queue.popleft()

            if current == end:
                path: list[tuple[int, int]] = []
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return path[::-1]

            row, col = current
            current_cell: MazeCell = maze[row][col]

            neighbors = []

            if current_cell.north and row > 0:
                neighbors.append((row - 1, col))
            if current_cell.south and row < height - 1:
                neighbors.append((row + 1, col))
            if current_cell.east and col < width - 1:
                neighbors.append((row, col + 1))
            if current_cell.west and col > 0:
                neighbors.append((row, col - 1))

            for neighbor in neighbors:
                if neighbor not in parent:
                    parent[neighbor] = current
                    queue.append(neighbor)

        return None

    def path_to_directions(self, path: list[tuple[int, int]]) -> list[str]:
        """Convert a path of coordinates
        to a list of directions (N, E, S, W)"""
        if not path or len(path) < 2:
            return []

        directions: list[str] = []
        for i in range(len(path) - 1):
            current: tuple[int, int] = path[i]
            next_pos: tuple[int, int] = path[i + 1]

            row_diff: int = next_pos[0] - current[0]
            col_diff: int = next_pos[1] - current[1]

            if row_diff == -1:
                directions.append("N")
            elif row_diff == 1:
                directions.append("S")
            elif col_diff == 1:
                directions.append("E")
            elif col_diff == -1:
                directions.append("W")

        return directions


class PathSolver:

    def __init__(
        self, maze_generator: type[MazeGenerator], algorithm: type[Finding]
    ) -> None:
        self.maze_generator: type[MazeGenerator] = maze_generator
        self.algorithm: type[Finding] = algorithm

    def solve(
        self,
        width: int,
        height: int,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> None:
        gen: MazeGenerator = self.maze_generator(width=width, height=height)
        maze: list[list[MazeCell]] = gen.generate_maze()

        algorithm: Finding = self.algorithm()
        path: list[tuple[int, int]] | None = algorithm.pathfind(
            maze, start, end
        )

        if path:
            print(f"Path found with {len(path)} steps:")
            directions: list[str] = algorithm.path_to_directions(path)
            print("Directions:", "".join(directions))
            print("Path coordinates:", path)
        else:
            print("No path found!")


def test_path_to_directions_roundtrip():
    path = [(0, 0), (0, 1), (1, 1)]
    assert BFS().path_to_directions(path) == ["E", "S"]


def main() -> None:
    try:
        solver: PathSolver = PathSolver(maze_generator=DFSearch, algorithm=BFS)
        solver.solve(width=2, height=2, start=(0, 0), end=(1, 1))
        test_path_to_directions_roundtrip()
    except Exception as e:
        print(f"Something went wrong -> {e}")


if __name__ == "__main__":
    main()
