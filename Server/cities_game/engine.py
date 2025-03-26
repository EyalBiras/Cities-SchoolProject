import json
import json
import logging
import logging.config
import time
import uuid
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from Server.cities_game.bot import Bot
from Server.cities_game.city import City
from Server.cities_game.game import Game
from Server.cities_game.images import ImagesType, player_type_to_images, TERRAIN_IMAGE, CITY_SIZE, CAPITAL_SIZE, \
    get_group_image, KNIGHT_SIZE
from Server.cities_game.player import Player
from Server.cities_game.player_type import PlayerType
from Server.cities_game.timeout import timeout
from Server.cities_game.turn_filter import TurnFilter
from Server.cities_game.update_flag import internal_update_flag

LOG_CONFIGURATION_FILE = Path(__file__).parent / "log.json"
GROUPS_DIRECTORY = Path(__file__).parent.parent / "groups"
TIME_LIMIT = 2000
WINDOW_SIZE = (1920, 1080)


def setup_logging(group: str, log_file: str, needs_logging=True) -> logging.Logger:
    logger = logging.getLogger(group)
    with open(LOG_CONFIGURATION_FILE, "r") as f:
        configuration = json.load(f)
    if not needs_logging:
        logger.addHandler(logging.NullHandler())
    else:
        configuration["handlers"]["file"]["filename"] = log_file
        print(configuration)
        configuration["loggers"][group] = {
            "level": "DEBUG",
            "handlers": [
                "file",
                "stderr"
            ]
        }
        logger.addFilter(TurnFilter(-1))
    logging.config.dictConfig(configuration)
    return logger


class CityNotFoundERROR(Exception):
    pass


class Engine:
    def __init__(self,
                 player: Player,
                 player_bot: Bot,
                 player_name: str,
                 enemy: Player,
                 enemy_bot: Bot,
                 enemy_name: str,
                 neutral: Player,
                 decorations: list[Image, tuple[int, int]],
                 game_name: str = "",
                 is_tournament: bool = True,
                 ) -> None:
        self.player = player
        self.player_bot = player_bot
        self.player_name = player_name
        self.player_actions = []
        self.player_time = 0
        if game_name == "":
            self.player_log_file = GROUPS_DIRECTORY / player_name / "battles" / enemy_name / "battle.log"
        else:
            self.player_log_file = GROUPS_DIRECTORY / player_name / "battles" / enemy_name / (game_name + ".log")
        self.player_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.player_log_file, "w") as f:
            pass
        self.player_logger = setup_logging(player_name, str(self.player_log_file), not is_tournament)
        self.s = set()
        self.enemy = enemy
        self.enemy_bot = enemy_bot
        self.enemy_name = enemy_name
        self.enemy_actions = []
        self.enemy_time = 0
        self.enemy_log_file = GROUPS_DIRECTORY / enemy_name / "battles" / player_name / "battle.log"
        self.enemy_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.enemy_log_file, "w") as f:
            pass
        self.enemy_logger = setup_logging(enemy_name, str(self.enemy_log_file), False)

        self.neutral = neutral
        self.winner = None
        self.turn = 1
        self.decorations = decorations
        self.is_tournament = is_tournament
        self.id = uuid.uuid4()
        self.player_logger.debug(str(self.id))
        self.game = [{"player": self.player.get_state(),
                      "enemy": self.enemy.get_state(),
                      "neutral": self.neutral.get_state()}]

    def create_game_player(self) -> Game:
        return Game(self.player, self.enemy, self.neutral, self.turn,
                    self.player_logger)

    def create_game_enemy(self) -> Game:
        return Game(self.enemy, self.player, self.neutral, self.turn,
                    self.enemy_logger)

    @lru_cache(maxsize=64)
    def check_city(self, city: City) -> bool:
        cities = self.player.cities + [self.player.capital_city]
        if city in cities:
            return True
        cities = self.enemy.cities + [self.enemy.capital_city]
        if city in cities:
            return True
        cities = self.neutral.cities
        if city in cities:
            return True
        raise CityNotFoundERROR()

    def check_action(self, action) -> bool:
        self.check_city(action[0])
        if action[1] == "send":
            self.check_city(action[2])
        return True

    def do_turn(self) -> None:
        player_game = self.create_game_player()
        try:
            with timeout(TIME_LIMIT):
                t_start = time.perf_counter()
                self.player_bot.do_turn(player_game)
            t_end = time.perf_counter()
            self.player_time += t_end - t_start
            player_actions = [city.action for city in player_game.player.cities]
            player_actions.append(player_game.player.capital_city.action)
            player_cities = [action[0] for action in player_actions if action is not None]
            if len(set(player_cities)) == len(player_cities):
                for action in player_actions:
                    if action is not None:
                        self.check_action(action)
                self.player_actions = player_actions
            else:
                self.player_actions = []

        except Exception as e:
            self.winner = "enemy"
            self.player_logger.exception("An error occurred")
            return
        except BaseException as e:
            self.winner = "enemy"
            self.player_logger.exception("An error occurred")
            return
        except TimeoutError as e:
            self.winner = "enemy"
            return

        enemy_game = self.create_game_enemy()

        try:
            with timeout(TIME_LIMIT):
                t_start = time.perf_counter()
                self.enemy_bot.do_turn(enemy_game)
            t_end = time.perf_counter()
            self.enemy_time += t_end - t_start
            enemy_actions = [city.action for city in enemy_game.player.cities]
            enemy_actions.append(enemy_game.player.capital_city.action)
            enemy_cities = [action[0] for action in enemy_actions if action is not None]
            if len(set(enemy_cities)) == len(enemy_cities):
                for action in enemy_actions:
                    if action is not None:
                        self.check_action(action)
                self.enemy_actions = enemy_actions
            else:
                self.enemy_actions = []
        except Exception as e:
            self.winner = "player"
            return
        except BaseException as e:
            self.winner = "player"
            return
        except OSError as e:
            self.winner = "player"
            return

    def update(self) -> None:
        self.do_turn()

        internal_update_flag.allow()

        self.player.update_groups()
        self.enemy.update_groups()
        self.player.update_cities(self.player_actions)
        self.enemy.update_cities(self.enemy_actions)
        self.neutral.update_cities([])
        self.player.update_lost_cities()
        self.enemy.update_lost_cities()
        self.neutral.update_lost_cities()
        self.player.update_conquered_cities()
        self.enemy.update_conquered_cities()

        internal_update_flag.disallow()

        self.game.append({
            "player": self.player.get_state(),
            "enemy": self.enemy.get_state(),
            "neutral": self.neutral.get_state()
        })

        if self.player.capital_city is None or self.player_time > TIME_LIMIT:
            self.winner = "enemy"
            if self.enemy.capital_city is None or self.enemy_time > TIME_LIMIT:
                self.winner = "draw"
        elif self.enemy.capital_city is None or self.enemy_time > TIME_LIMIT:
            self.winner = "player"
        if self.turn == 300 and self.winner is None:
            if len(self.player.cities) > len(self.enemy.cities):
                self.winner = "player"
            elif len(self.enemy.cities) > len(self.player.cities):
                self.winner = "enemy"
            else:
                self.winner = "draw"
        self.turn += 1

    @staticmethod
    def draw_player(player: Player,
                    image: Image,
                    draw: ImageDraw,
                    font: ImageFont,
                    kind: PlayerType,
                    group_color) -> None:

        for city in player.cities:
            city_image = player_type_to_images[kind][ImagesType.CITY]
            image.paste(city_image,
                        (int(city.position[0]) - CITY_SIZE[0] // 2, int(city.position[1]) - CITY_SIZE[1] // 2),
                        city_image.getchannel('A'))
            draw.text((city.position[0], city.position[1] - CITY_SIZE[1] // 2), f"{city.people_amount}",
                      fill=group_color,
                      font=font)
        for group in player.groups:
            group_image = get_group_image(kind, group.people_amount)[group.animation_phase]
            image.paste(group_image, (int(group.position[0]), int(group.position[1])),
                        group_image.getchannel('A'))
            draw.text((group.position[0] + group_image.size[0] // 2, group.position[1] - KNIGHT_SIZE[1] // 2),
                      f"{group.people_amount}", fill=group_color,
                      font=font)
        capital = player.capital_city
        if capital:
            capital_city_image = player_type_to_images[kind][ImagesType.CAPITAL]
            image.paste(capital_city_image, (
                int(capital.position[0]) - CAPITAL_SIZE[0] // 2, int(capital.position[1]) - CAPITAL_SIZE[1] // 2),
                        capital_city_image.getchannel('A'))
            draw.text((capital.position[0], capital.position[1] - CAPITAL_SIZE[0] // 2), f"{capital.people_amount}",
                      fill=group_color,
                      font=font)

    def draw_decoration(self, image: Image):
        for decoration, position in self.decorations:
            image.paste(decoration, position, decoration.getchannel('A'))

    def draw_turn(self) -> Image:
        image = Image.new('RGB', WINDOW_SIZE)
        for x in range(0, WINDOW_SIZE[0], TERRAIN_IMAGE.width):
            for y in range(0, WINDOW_SIZE[1], TERRAIN_IMAGE.height):
                image.paste(TERRAIN_IMAGE, (x, y))
        image = image.filter(ImageFilter.GaussianBlur(1))
        draw = ImageDraw.Draw(image)

        font = ImageFont.load_default(size=20)
        names_font = ImageFont.load_default(size=30)
        draw.text((0, 0), f"{self.player_name}", fill="black", font=names_font)
        text_box = names_font.getbbox(self.enemy_name)
        text_width = text_box[2] - text_box[0]
        draw.text((WINDOW_SIZE[0] - text_width, 0), f"{self.enemy_name}", fill="black", font=names_font)
        self.draw_player(self.player, image, draw, font, PlayerType.PLAYER, "blue")
        self.draw_player(self.enemy, image, draw, font, PlayerType.ENEMY, "red")
        self.draw_player(self.neutral, image, draw, font, PlayerType.NEUTRAL, "black")
        self.draw_decoration(image)

        if self.winner is not None:
            font = ImageFont.load_default(100)
            if self.winner == "player":
                self.winner = self.player_name
                draw.text((150, 250), f"{self.player_name} won", fill="black", font=font)
            elif self.winner == "enemy":
                self.winner = self.enemy_name
                draw.text((150, 250), f"{self.enemy_name} won", fill="black", font=font)
            else:
                draw.text((150, 250), f"draw", fill="black", font=font)

        return image

    def make_video(self) -> tuple[list[Image], str]:
        images = []
        while self.winner is None:
            images.append(self.draw_turn())
        print(self.winner)
        logging.shutdown()
        if self.winner is not None:
            if self.winner == "player":
                self.winner = self.player_name
            elif self.winner == "enemy":
                self.winner = self.enemy_name
            else:
                self.winner = "draw"
        return images, self.winner

    def make_game(self):
        while self.winner is None:
            self.update()

        if self.winner is not None:
            if self.winner == "player":
                self.winner = self.player_name
            elif self.winner == "enemy":
                self.winner = self.enemy_name
            else:
                self.winner = "draw"

        game = {"id": str(self.id),
                "game": self.game,
                "winner": self.winner}
        for handler in self.player_logger.handlers:
            handler.close()
            self.player_logger.removeHandler(handler)
        for handler in self.enemy_logger.handlers:
            handler.close()
            self.enemy_logger.removeHandler(handler)
        logging.shutdown()
        return game, self.winner
