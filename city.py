from __future__ import annotations

from typing import Self

import numpy as np


class City:
    def __init__(self, people_amount: int, level: int, position: np.ndarray[int]) -> None:
        self.__people_amount = people_amount
        self.__level = level
        self.__action = None
        self.__position = position

    @property
    def people_amount(self):
        return self.__people_amount

    @people_amount.setter
    def people_amount(self, value):
        self.__people_amount = value


    @property
    def position(self):
        return self.__position

    def get_distance_to(self, destination: City):
        return np.linalg.norm(destination.position - self.position)

    def get_turns_till_arrival(self, destination: City):
        return np.ceil(self.get_distance_to(destination) / 4)

    def can_send_groups(self, people_amount: int) -> bool:
        return people_amount < self.__people_amount

    def send_group(self, destination: Self, people_amount: int) -> None:
        if self.can_send_groups(people_amount):
            self.__action = ["send", self, destination, people_amount]

    def get_upgrade_cost(self) -> int:
        return 20

    def can_upgrade(self) -> bool:
        return self.get_upgrade_cost() < self.__people_amount and self.__level < 4

    def upgrade(self):
        if self.can_upgrade():
            self.__action = ["upgrade"]

    def update(self) -> None:
        self.__people_amount += self.__level
