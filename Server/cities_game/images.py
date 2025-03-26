from enum import StrEnum
from enum import StrEnum
from pathlib import Path

from PIL import Image, ImageOps

from Server.cities_game.player_type import PlayerType


class ImagesType(StrEnum):
    CITY = "City"
    CAPITAL = "Capital"
    KNIGHT = "Knight"
    TILE = "Tile"


def format_image(image_file: Path, size: tuple[int, int] | None = None, reflect: bool = False) -> Image:
    image = Image.open(image_file)
    if reflect:
        image = ImageOps.mirror(image)
    if size is not None:
        image = image.resize(size, resample=Image.Resampling.LANCZOS)
    image.convert('RGBA')
    return image


def concat_horizontally(image: Image, count: int) -> Image:
    width, height = image.size
    new_width = width * count
    new_height = height
    new_image = Image.new("RGBA", (new_width, new_height))
    for i in range(count):
        new_image.paste(image, (i * width, 0))
    return new_image


def concat_vertically(image: Image, count: int) -> Image:
    width, height = image.size
    new_width = width
    new_height = height * count
    new_image = Image.new("RGBA", (new_width, new_height))
    for i in range(count):
        new_image.paste(image, (0, i * height))
    return new_image


def make_group(image: Image, count: int) -> Image:
    if count == 1:
        return image
    if count == 2:
        return concat_horizontally(image, 2)
    if count == 3:
        width, height = image.size
        new_width = width * 2
        new_height = height * 2
        concat_image = concat_horizontally(image, 2)
        new_image = Image.new("RGBA", (new_width, new_height))
        new_image.paste(concat_image, (0, height))
        new_image.paste(image, (width // 2, 0))
        return new_image
    if count == 4:
        return concat_vertically(concat_horizontally(image, 2), 2)
    if count == 5:
        width, height = image.size
        new_width = width * 3
        new_height = height * 2
        concat_image = make_group(image, 4)
        new_image = Image.new("RGBA", (new_width, new_height))
        new_image.paste(concat_image, (0, 0))
        new_image.paste(image, (width * 2, height // 2))
        return new_image
    if count == 6:
        return concat_vertically(concat_horizontally(image, 3), 2)


def get_knight(image_file: Path, size: tuple[int, int] | None = None, reflect: bool = False, count: int = 1) -> list[
    Image]:
    animation = []
    for warrior_image in image_file.glob("*"):
        if "Warrior_walk_animation" in warrior_image.name:
            animation.append(make_group(format_image(warrior_image, size, reflect), count=count))
    return animation


def load_images(image_directory: Path) -> list[Image]:
    return [format_image(image_file) for image_file in image_directory.glob("*")]


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

KNIGHT_SIZE = (int(get_knight(PLAYER_KNIGHT_FILE)[0].size[0] // 2), int(get_knight(PLAYER_KNIGHT_FILE)[1].size[1] // 2))

player_type_to_images = {
    PlayerType.PLAYER:
        {
            ImagesType.CITY: format_image(PLAYER_CITY_FILE),
            ImagesType.CAPITAL: format_image(PLAYER_CAPITAL_FILE),
            ImagesType.KNIGHT: [get_knight(PLAYER_KNIGHT_FILE, KNIGHT_SIZE, False, count) for count in range(1, 7)]
        },
    PlayerType.ENEMY:
        {
            ImagesType.CITY: format_image(ENEMY_CITY_FILE),
            ImagesType.CAPITAL: format_image(ENEMY_CAPITAL_FILE),
            ImagesType.KNIGHT: [get_knight(ENEMY_KNIGHT_FILE, KNIGHT_SIZE, True, count) for count in range(1, 7)]
        },
    PlayerType.NEUTRAL:
        {
            ImagesType.CITY: format_image(NEUTRAL_CITY_FILE),
            ImagesType.CAPITAL: format_image(NEUTRAL_CAPITAL_FILE)
        }
}
TERRAIN_IMAGE = Image.open(TERRAIN_FILE)
CITY_SIZE = player_type_to_images[PlayerType.PLAYER][ImagesType.CITY].size
CAPITAL_SIZE = player_type_to_images[PlayerType.PLAYER][ImagesType.CAPITAL].size

decorations = {
    "decorations": load_images(DECORATIONS_DIRECTORY),
    "trees": 2,
    "sheep": 3,
}


def get_group_image(kind: PlayerType, people_amount: int) -> Image:
    people_amount -= 1
    if people_amount > 5:
        people_amount = 5
    return player_type_to_images[kind][ImagesType.KNIGHT][people_amount]
