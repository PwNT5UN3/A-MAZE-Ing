from numpy import random as nprand


class MazeGenerator:
    '''The core maze generator'''
    def __init__(self, *, seed: int | None = None) -> None:
        if seed is None:
            seed = nprand.random_integers(0, high=2147483647)
        self.rng = nprand.Generator(nprand.MT19937(seed=seed))


gen = MazeGenerator(seed=42)
print(gen.rng.random(1))