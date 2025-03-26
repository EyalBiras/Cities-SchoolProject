from Server.cities_game.capital_city import Capital
from Server.cities_game.city import City
from Server.cities_game.group import Group
from Server.cities_game.update_flag import internal_update_flag


class Player:
    def __init__(self, cities: list[City], capital_city: Capital | None, groups: list[Group]) -> None:
        self.__cities = cities
        self.__capital_city = capital_city
        self.__groups = groups
        self.__conquered_cities = []
        self.__lost_cities = []

    @property
    def groups(self):
        return self.__groups

    @property
    def capital_city(self):
        return self.__capital_city

    @property
    def cities(self):
        return self.__cities

    def update_groups(self) -> None:
        if internal_update_flag.is_allowed():
            for group in self.__groups:
                group.update()
                if group.turns_till_arrival == 0:
                    if group.destination in self.cities or group.destination is self.__capital_city:
                        group.destination.people_amount += group.people_amount
                    else:
                        group.destination.people_amount -= group.people_amount
                        if group.destination.people_amount < 0 and group.destination not in self.__conquered_cities:
                            self.__conquered_cities.append(group.destination)
                    self.__groups.remove(group)

    def update_cities(self, actions) -> None:
        if internal_update_flag.is_allowed():
            for city in self.__cities:
                if city.people_amount < 0:
                    self.__lost_cities.append(city)
                else:
                    city.update()
            for action in actions:
                try:
                    if action is None:
                        continue
                    city = action[0]
                    if action[1] == "send":
                        if city != action[2]:
                            self.__groups.append(Group(action[3], city, action[2], city.position))

                except ValueError:
                    pass

            if self.__capital_city is not None:
                if self.__capital_city.people_amount < 0:
                    self.__capital_city = None
                else:
                    self.__capital_city.update()

    def update_lost_cities(self) -> None:
        if internal_update_flag.is_allowed():
            for city in self.__lost_cities:
                self.cities.remove(city)
            self.__lost_cities = []

    def update_conquered_cities(self):
        if internal_update_flag.is_allowed():
            for city in self.__conquered_cities:
                city.people_amount *= -1
                print(city.level)
                if city.level == 0:
                    city.level = 1
                self.cities.append(city)
            self.__conquered_cities = []

    def get_state(self):
        if self.__capital_city:
            state = {
                "cities": [(city.people_amount, city.level, (int(city.position[0]), int(city.position[1]))) for city in
                           self.__cities],
                "capital": [(self.__capital_city.people_amount, self.__capital_city.level,
                             ((int(self.__capital_city.position[0])), int(self.__capital_city.position[1])))],
                "groups": [(group.people_amount, (int(group.position[0]), int(group.position[1])),
                            get_direction(group.source.position[0], group.destination.position[0])) for group in
                           self.__groups],
            }
        else:
            state = {
                "cities": [(city.people_amount, city.level, (int(city.position[0]), int(city.position[1]))) for city in
                           self.__cities]
            }
        return state


def get_direction(source_x, destination_x):
    direction = destination_x - source_x
    if direction < 0:
        return -1
    return 1
