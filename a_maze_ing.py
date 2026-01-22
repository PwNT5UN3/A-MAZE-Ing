from sys import argv
from config_reader import read_config
from render import interactive_maze_app
from mazegen import DFSearch, WilsonsAlgorithm
from bfs import BFS


def get_int_int_tuple(val_1: int, val_2: int) -> tuple[int, int]:
    return tuple[int, int]((val_1, val_2))


def main() -> None:
    if len(argv) < 2:
        print("No config file given. Aborting...")
        return
    config = argv[1]
    try:
        file = open(config)
        if not file.readable():
            file.close()
            raise PermissionError("")
        file.close()
    except FileNotFoundError:
        print("Config file does not exist. Aborting...")
        return
    except PermissionError:
        print("Config file cannot be read. Aborting...")
        return
    configs = read_config(config)
    print(configs)
    if configs["algorithm"] == "dfs":
        gen: type[DFSearch | WilsonsAlgorithm] = DFSearch
    else:
        gen = WilsonsAlgorithm
    interactive_maze_app(
        height=configs["height"],
        width=configs["width"],
        entry=tuple[int, int](
            (int(configs["entry.x"]), int(configs["entry.y"]))
        ),
        end=tuple[int, int]((int(configs["exit.x"]), int(configs["exit.y"]))),
        maze_generator_cls=gen,
        pathfinder_cls=BFS,
        seed=int(configs["seed"]),
        perfect=configs["perfect"],
        output=str(configs["output_file"]),
    )


# gen2 = DFSearch(50, 50)
# maze2 = gen2.generate_maze()
# check_perfection(gen, maze)
# check_perfection(gen2, maze2)


if __name__ == "__main__":
    main()
