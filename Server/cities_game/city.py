from __future__ import annotations

import uuid
from functools import lru_cache

import numpy as np

from Server.cities_game.update_flag import internal_update_flag


class City:
    def __init__(self, people_amount: int, level: int, position: np.ndarray[float]) -> None:
        self.__people_amount = people_amount
        self.__level = level
        self.__action = None
        self.__position = position.astype(float)
        self.__id = uuid.uuid4()

    @property
    def id(self):
        return self.__id

    @property
    def level(self) -> int:
        return self.__level

    @level.setter
    def level(self, value: int) -> None:
        if internal_update_flag.is_allowed():
            self.__level = value

    @property
    def action(self):
        return self.__action

    @property
    def people_amount(self) -> int:
        return self.__people_amount

    @people_amount.setter
    def people_amount(self, value: int) -> None:
        if internal_update_flag.is_allowed():
            self.__people_amount = value

    @property
    def position(self) -> np.ndarray[float]:
        return self.__position

    @lru_cache(maxsize=16)
    def get_distance_to(self, destination: City) -> float:
        return float(np.linalg.norm(destination.position - self.position))

    @lru_cache(maxsize=16)
    def get_turns_till_arrival(self, destination: City) -> int:
        return np.ceil(self.get_distance_to(destination) / 40)

    def can_send_group(self, people_amount: int) -> bool:
        return people_amount < self.__people_amount and self.action is None and people_amount > 0

    def send_group(self, destination: City, people_amount: int) -> None:
        if self.can_send_group(people_amount):
            self.__people_amount -= people_amount
            self.__action = [self, "send", destination, people_amount]

    def get_upgrade_cost(self) -> int:
        return self.__level * 30

    def can_upgrade(self) -> bool:
        return self.get_upgrade_cost() < self.__people_amount and self.__level < 4 and self.action is None

    def upgrade(self) -> None:
        if self.can_upgrade():
            self.people_amount -= self.get_upgrade_cost()
            self.__action = [self, "upgrade"]

    def update(self) -> None:
        if internal_update_flag.is_allowed():
            self.__action = None
            self.__people_amount += self.__level

    def __hash__(self):
        return hash(self.__id)

    def __eq__(self, other: City) -> bool:
        return self.__id == other.id
