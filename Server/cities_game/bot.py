from abc import ABC, abstractmethod

from Server.cities_game.game import Game

TIME_LIMIT = 2


class Bot(ABC):
    @abstractmethod
    def do_turn(self, game: Game) -> None:
        pass
