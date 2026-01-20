import pytest
from src.maze_generator.maze_gen import MazeCell, WilsonsAlgorithm


def test_constructor_preserves_width_height_order():
    gen = WilsonsAlgorithm(14, 10, seed=1)
    # public args (width=14, height=10) must be reflected on the instance
    assert gen.width == 14
    assert gen.height == 10


def test_42_pattern_fits_when_available():
    g = WilsonsAlgorithm(14, 10, seed=1)
    g.generate_maze()
    assert len(g.pattern_coordinates) == 18
    assert all(
        0 <= r < g.height and 0 <= c < g.width
        for r, c in g.pattern_coordinates
    )


def test_cell_map_lookup_and_accessor_consistency():
    gen = WilsonsAlgorithm(10, 15, seed=1)
    gen.generate_maze()

    # sample coords: corners + center
    samples = [
        (0, 0),
        (0, gen.width - 1),
        (gen.height - 1, 0),
        (gen.height - 1, gen.width - 1),
        (gen.height // 2, gen.width // 2),
    ]

    for coord in samples:
        # dict lookup
        cell = gen.cell_map[coord]
        assert isinstance(cell, MazeCell)
        assert cell.coordinates == coord

        # accessor consistency (should return the exact same object)
        assert gen.get_maze_cell_from_coordinate(coord) is cell

    # out-of-bounds: dict raises KeyError; accessor raises ValueError
    oob = (gen.height + 5, gen.width + 5)
    with pytest.raises(KeyError):
        _ = gen.cell_map[oob]
    with pytest.raises(ValueError):
        gen.get_maze_cell_from_coordinate(oob)


test_cell_map_lookup_and_accessor_consistency()
test_42_pattern_fits_when_available()
test_constructor_preserves_width_height_order()

# pytest -q tests/test_cell_lookup.py
