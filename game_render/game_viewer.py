import random
import sys
import sys
import time
from pathlib import Path
import pygame.freetype
import numpy as np
import pygame
from PIL import Image, ImageFilter
from log_viewer import LogViewer
from game_render.images import BLACK, BLUE, RED, GREEN
from images import get_group_image

IMAGES_BASE_FILE = Path(__file__).parent.parent / "Tiny Swords" / "Tiny Swords (Update 010)"
DECORATIONS_DIRECTORY = IMAGES_BASE_FILE / "Deco"
RESOURCES_DIRECTORY = IMAGES_BASE_FILE / "Resources"

TERRAIN_FILE = IMAGES_BASE_FILE / "Terrain" / "Ground" / "green_tile.png"
ASSETS_BASE_FILE = IMAGES_BASE_FILE / "Factions" / "Knights"

PLAYER_CITY_FILE = ASSETS_BASE_FILE / "Buildings" / "Tower" / "Tower_Blue.png"
PLAYER_CAPITAL_FILE = ASSETS_BASE_FILE / "Buildings" / "Castle" / "Castle_Blue.png"
PLAYER_KNIGHT_FILE = ASSETS_BASE_FILE / "Troops" / "Warrior" / "Blue"

ENEMY_CITY_FILE = ASSETS_BASE_FILE / "Buildings" / "Tower" / "Tower_Red.png"
ENEMY_CAPITAL_FILE = ASSETS_BASE_FILE / "Buildings" / "Castle" / "Castle_Red.png"
ENEMY_KNIGHT_FILE = ASSETS_BASE_FILE / "Troops" / "Warrior" / "Red"

NEUTRAL_CITY_FILE = ASSETS_BASE_FILE / "Buildings" / "Tower" / "Tower_yellow.png"
NEUTRAL_CAPITAL_FILE = ASSETS_BASE_FILE / "Buildings" / "Castle" / "Castle_yellow.png"


FILE = Path(__file__)
WINDOW_SIZE = (1920, 1080)
def load_image(image_path: Path, size: tuple[int, int] | None = None):
    image = pygame.image.load(image_path).convert()
    image.set_colorkey((0, 0, 0))
    if size is not None:
        image = pygame.transform.scale(image, size)
    return image


def load_images(images_directory: Path, size: tuple[int, int] | None = None):
    images = []
    for image_path in images_directory.glob("*"):
        images.append(load_image(image_path, size))
    return images


def apply_gaussian_blur(pygame_surface):
    arr = pygame.surfarray.array3d(pygame_surface)
    pil_image = Image.fromarray(np.transpose(arr, (1, 0, 2)))

    pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=0.5))

    arr = np.array(pil_image)
    pygame_surface = pygame.surfarray.make_surface(np.transpose(arr, (1, 0, 2)))

    return pygame_surface


class GameRender:
    def __init__(self, game, winner, log_entries = None):
        WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
        print(WIDTH, HEIGHT)
        pygame.display.set_caption("Map Editor")
        self.font = pygame.font.SysFont(None, 36)
        self.group_font = pygame.font.SysFont(None, 27)
        self.won_font = pygame.font.SysFont(None, 100)
        self.paused_font = pygame.font.SysFont(None, 60)
        self.log_entries = log_entries
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.display = pygame.Surface(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.game = game
        self.assets = [load_images(DECORATIONS_DIRECTORY),
                       [load_image(NEUTRAL_CAPITAL_FILE), load_image(NEUTRAL_CITY_FILE)]]
        self.player_assets = [load_image(PLAYER_CAPITAL_FILE), load_image(PLAYER_CITY_FILE)]
        self.enemy_assets = [load_image(ENEMY_CAPITAL_FILE), load_image(ENEMY_CITY_FILE)]
        self.is_paused = False
        self.fps = 6
        self.previous = time.perf_counter()
        self.turn = 0
        self.background = pygame.Surface(WINDOW_SIZE)
        self.winner = winner
        image = pygame.image.load(TERRAIN_FILE).convert()
        image.set_colorkey((0, 0, 0))
        for x in range(0, WINDOW_SIZE[0], image.width):
            for y in range(0, WINDOW_SIZE[1], image.height):
                self.background.blit(image, (x, y))
        self.background = apply_gaussian_blur(self.background)
        self.back = self.font.render(f"Back", True, (0, 0, 0))
        self.back_button = pygame.Rect(0, 100, self.back.get_width(), self.back.get_height())

    def render_text(self, text, x, y, color):
        text_surface = self.font.render(text, True, color)
        self.display.blit(text_surface, (x, y))

    def render_turn(self):
        self.display.fill((0, 0, 0))

        if self.turn >= len(self.game) - 1:
            self.turn = len(self.game) - 2
        turn = self.game[self.turn]
        self.display.blit(self.background)

        self.render_text(f"FPS: {self.fps}, current turn :{self.turn}", WINDOW_SIZE[0] // 2 - 30, 0, (255, 255, 255))

        for p, t in turn.items():
            if p == "player":
                color = BLUE
            elif p == "enemy":
                color = RED
            else:
                color = BLACK
            for city in t["cities"]:
                if p == "player":
                    city_image = self.player_assets[1]
                elif p == "enemy":
                    city_image = self.enemy_assets[1]
                else:
                    city_image = self.assets[1][1]
                city_position = city[2]
                size = city_image.size
                self.display.blit(city_image,
                                  (int(city_position[0]) - size[0] // 2, int(city_position[1]) - size[1] // 2))
                city_info_surface = self.font.render(f"Total Soldiers: {city[0]}\nLevel: {city[1]}", True, color)
                self.display.blit(city_info_surface, (int(city_position[0]) - size[0] // 2, int(city_position[1]) - size[1] // 2))


            if p != "neutral":
                if p == "player":
                    capital_image = self.player_assets[0]
                elif p == "enemy":
                    capital_image = self.enemy_assets[0]
                capital = t["capital"][0]
                capital_position = t["capital"][0][2]
                size = capital_image.size
                self.display.blit(capital_image,
                                  (int(capital_position[0]) - size[0] // 2, int(capital_position[1]) - size[1] // 2))
                capital_info_surface = self.font.render(f"  Total Soldiers: {capital[0]}\n  Level: {capital[1]}", True, color)
                self.display.blit(capital_info_surface,
                                  (int(capital_position[0]) - size[0] // 2, int(capital_position[1]) - size[1] // 2))
                for group in t["groups"]:
                    print(group)
                    animation_phase = random.randint(0,5)
                    if p == "player":
                        if group[2] == 1:
                            reflect = False
                        else:
                            reflect = True
                        group_image = get_group_image("player", group[0], reflect=reflect)[animation_phase]
                    else:
                        if group[2] == 1:
                            reflect = False
                        else:
                            reflect = True
                        group_image = get_group_image("enemy", group[0], reflect=reflect)[animation_phase]
                    size = group_image.size
                    self.display.blit(group_image, group[1])
                    group_info = self.group_font.render(f"Total Soldiers: {group[0]}",
                                                            True, color)
                    self.display.blit(group_info,
                                      (
                                      int(group[1][0]) - size[0] // 2, int(group[1][1]) - size[1] // 2))
        if self.turn == len(self.game) - 2:
            text_surface = self.won_font.render(f"{self.winner} Won!", True, (255, 215, 0))
            self.display.blit(text_surface, (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 100))

    def run(self):
        while True:

            if time.perf_counter() - self.previous > 1 / self.fps:
                self.render_turn()
                self.previous = time.perf_counter()
                l = LogViewer(self.log_entries, screen_width - 100, 0, 100, screen_height, self.font)
                l.print_log_entries(self.turn)
                if not self.is_paused:
                    self.turn += 1
                else:
                    self.render_text("Game Paused", WINDOW_SIZE[0] // 2 - 10, 30, BLACK)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    if event.key == pygame.K_UP:
                        self.fps += 1
                        self.fps %= 60
                    if event.key == pygame.K_DOWN:
                        self.fps -= 1
                        if self.fps <= 0:
                            self.fps = 1
                    if event.key == pygame.K_RIGHT:
                        self.turn += self.fps
                    if event.key == pygame.K_LEFT:
                        self.turn -= self.fps
                        if self.turn < 0:
                            self.turn = 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.back_button.collidepoint(pygame.mouse.get_pos()):
                            return

            screen_width, screen_height = self.screen.get_size()



            # if self.log_entries:
            #     display = pygame.transform.smoothscale(self.display, (screen_width - 100, screen_height))
            #     l = LogViewer(self.log_entries, screen_width - 100, 0, 100, screen_height ,self.font)
            #     print(self.log_entries)
            #     l.draw(1, self.screen, BLUE)
            # else:
            #     display = pygame.transform.smoothscale(self.display, (screen_width, screen_height))

            display = pygame.transform.smoothscale(self.display, (screen_width, screen_height))

            self.screen.blit(display)
            pygame.draw.rect(self.screen, (100, 0, 200), self.back_button, 2)
            self.screen.blit(self.back, (0, 100))
            pygame.display.update()
            self.clock.tick(60)
