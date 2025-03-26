import json
import sys
from pathlib import Path

import pygame

from Server.cities_game.images import DECORATIONS_DIRECTORY, NEUTRAL_CAPITAL_FILE, NEUTRAL_CITY_FILE
from Server.map_editor.tile import Tile

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


def load_decoration(decoration_directory: Path):
    images = []
    for image_path in decoration_directory.glob("*"):
        images.append(image_path)
    return images


def distance(position1: tuple[int, int], position2: tuple[int, int]) -> float:
    return ((position1[0] - position2[0]) ** 2 + (position1[1] - position2[1]) ** 2) ** 0.5


def get_min_distance(size: tuple[int, int]) -> float:
    return ((size[0] // 2) ** 2 + (size[1] // 2) ** 2) ** 0.5


def save_map(tower_map):
    with open("test.json", "w") as f:
        json.dump(tower_map, f, indent=2)


def get_minimal_distance(size1, size2) -> bool:
    return 0.25 * ((size1[0] + size2[0]) ** 2 + (size1[1] + size2[1]) ** 2) ** 0.5


def reflect(position):
    return (WINDOW_SIZE[0] - position[0], position[1])


class Editor:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Map Editor")
        self.screen = pygame.display.set_mode((1920, 1080))
        self.display = pygame.Surface((1920, 1080))
        self.clock = pygame.time.Clock()

        self.decorations = load_decoration(DECORATIONS_DIRECTORY)
        self.buildings = [Tile.CAPITAL, Tile.CITY]
        self.decorations_list = [(image, Tile.DECORATION) for image in load_images(DECORATIONS_DIRECTORY)]
        self.bar = [load_images(DECORATIONS_DIRECTORY),
                    [load_image(NEUTRAL_CAPITAL_FILE, size=(100, 100)), load_image(NEUTRAL_CITY_FILE, size=(100, 100))]]
        self.assets = [load_images(DECORATIONS_DIRECTORY),
                       [load_image(NEUTRAL_CAPITAL_FILE), load_image(NEUTRAL_CITY_FILE)]]
        self.category = 0
        self.index = 0
        self.clicking = False
        self.shift = False
        self.assets_map = {}
        self.decorations_map = []
        self.buildings_map = []

    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            current_tile_image = self.bar[self.category][self.index]
            asset = self.assets[self.category][self.index]
            current_tile_image.set_alpha(100)

            mouse_position = pygame.mouse.get_pos()
            position = (mouse_position[0] - asset.size[0] // 2, mouse_position[1] - asset.size[1] // 2)
            print(position)
            self.display.blit(asset, position)
            self.display.blit(current_tile_image, (0, 0))
            pygame.draw.line(self.display, "yellow", (WINDOW_SIZE[0] // 2, 0), (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1]))
            for position, asset in self.assets_map.items():
                self.display.blit(asset, position)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    a = {
                        "decorations": self.decorations_map,
                        "buildings": self.buildings_map
                    }
                    save_map(a)
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.index = 0
                            self.category = (self.category + 1) % len(self.bar)
                        if event.button == 5:
                            self.index = 0
                            self.category = (self.category - 1) % len(self.bar)
                    else:
                        if event.button == 4:
                            self.index = (self.index + 1) % len(self.bar[self.category])
                        if event.button == 5:
                            self.index = (self.index - 1) % len(self.bar[self.category])

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False

                if self.clicking:
                    asset = self.assets[self.category][self.index]
                    position = (mouse_position[0] - asset.size[0] // 2, mouse_position[1] - asset.size[1] // 2)
                    can = True
                    for p, ase in self.assets_map.items():
                        if self.category == 0:
                            if distance(p, position) < get_minimal_distance(asset.size, ase.size):
                                can = False
                                break
                        elif self.category == 1:
                            r2 = reflect(mouse_position)
                            r = (r2[0] - asset.size[0] // 2, r2[1] - asset.size[1] // 2)
                            if distance(p, position) < get_minimal_distance(asset.size, ase.size) or distance(r,
                                                                                                              p) < get_minimal_distance(
                                    asset.size, ase.size):
                                can = False
                                break
                    if can:
                        self.assets_map[position] = asset
                        if self.category == 0:
                            self.decorations_map.append((str(self.decorations[self.index]), position))
                        elif self.category == 1:
                            r2 = reflect(mouse_position)
                            r = (r2[0] - asset.size[0] // 2, r2[1] - asset.size[1] // 2)
                            self.assets_map[r] = asset
                            self.buildings_map.append((self.buildings[self.index], mouse_position))
                            self.buildings_map.append((self.buildings[self.index], r2))

            self.screen.blit(self.display)
            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    e = Editor()
    e.run()