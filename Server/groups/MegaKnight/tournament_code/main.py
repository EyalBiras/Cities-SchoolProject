from cities_game import Game, Group, Bot

class MyBot(Bot):
    def do_turn(self, game: Game) -> None:
        if game.turn < 20:
            capital = game.get_my_city_capital()
            neutral_cities = game.get_neutral_cities()
            if neutral_cities:
                neutral_cities.sort(key=lambda x: capital.get_turns_till_arrival(x))
                c = neutral_cities[0]
                sent = False
                for city in game.get_my_cities():
                    if city.people_amount > c.people_amount:
                        city.send_group(c, c.people_amount + 1)
                        sent = True
                if not sent:
                    capital.send_group(c, c.people_amount + 1)
        for city in game.get_my_cities():
            city.send_group(game.get_my_city_capital(), city.people_amount - 1)