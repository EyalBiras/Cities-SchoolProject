from cities_game import Game, Group, Bot

class MyBot(Bot):
    def do_turn(self, game: Game) -> None:
        if game.get_my_city_capital().people_amount > game.get_enemy_city_capital().people_amount:
            game.get_my_city_capital().send_group(game.get_enemy_city_capital(), game.get_my_city_capital().people_amount - 1)
