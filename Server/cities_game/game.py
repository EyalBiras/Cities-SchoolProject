import logging

from Server.cities_game.capital_city import Capital
from Server.cities_game.city import City
from Server.cities_game.group import Group
from Server.cities_game.player import Player
from Server.cities_game.turn_filter import TurnFilter


class Game:
    def __init__(self, player: Player, enemy: Player, neutral: Player, turn: int, logger: logging.Logger) -> None:
        self.__player = player
        self.__enemy = enemy
        self.__neutral = neutral
        self.__turn = turn
        self.__logger = logger
        self.__logger.addFilter(TurnFilter(self.__turn))

    @property
    def logger(self):
        return self.__logger

    @property
    def enemy(self):
        return self.__enemy

    @property
    def player(self):
        return self.__player

    def get_enemy_cities(self) -> list[City]:
        return self.__enemy.cities.copy()

    def get_enemy_city_capital(self) -> Capital:
        return self.__enemy.capital_city

    def get_enemy_groups(self) -> list[Group]:
        return self.__enemy.groups.copy()

    def get_my_cities(self) -> list[City]:
        return self.__player.cities.copy()

    def get_my_city_capital(self) -> Capital:
        return self.__player.capital_city

    def get_my_groups(self) -> list[Group]:
        return self.__player.groups

    def get_neutral_cities(self) -> list[City]:
        return self.__neutral.cities.copy()

    @property
    def turn(self):
        return self.__turn
