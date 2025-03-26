import numpy as np

from Server.cities_game.city import City


class Capital(City):
    def __init__(self, people_amount: int, level: int, position: np.ndarray[float]) -> None:
        super().__init__(people_amount, level, position)
