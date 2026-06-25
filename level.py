# Описание локаций и отрисовка их фона.
import pygame

import config
from config import (
    BLUE,
    GRAY,
    HEIGHT,
    LIGHT_GREEN,
    SAND,
    WIDTH,
    load_background_image,
)
from game.enemy import FastEnemy, NormalEnemy, RandomEnemy, TankEnemy


LEVELS = [
    {
        "name": "Зелёное поле",
        "background": BLUE,
        "accent": LIGHT_GREEN,
        "texture": "location_green_field.png",
        "rounds": 2,
        "enemy_classes": [NormalEnemy, RandomEnemy]
    },
    {
        "name": "Песчаная зона",
        "background": (80, 130, 150),
        "accent": SAND,
        "texture": "location_sand_zone.png",
        "rounds": 2,
        "enemy_classes": [FastEnemy, NormalEnemy, RandomEnemy]
    },
    {
        "name": "Серая база",
        "background": (60, 70, 95),
        "accent": GRAY,
        "texture": "location_gray_base.png",
        "rounds": 3,
        "enemy_classes": [TankEnemy, FastEnemy, NormalEnemy, RandomEnemy]
    }
]


def draw_level_background(level):
    # Основной вариант: полноэкранная текстура уровня из папки assets.
    screen = config.screen
    texture_name = level.get("texture")

    if texture_name is not None:
        texture = load_background_image(texture_name)

        if texture is not None:
            screen.blit(texture, (0, 0))
            return

    # Запасной вариант, если файл текстуры удалён или не загрузился.
    screen.fill(level["background"])

    if level["name"] == "Зелёное поле":
        pygame.draw.rect(screen, level["accent"], (0, 450, WIDTH, 150))
        pygame.draw.circle(screen, (40, 150, 70), (680, 120), 70)

    elif level["name"] == "Песчаная зона":
        pygame.draw.rect(screen, level["accent"], (0, 420, WIDTH, 180))
        pygame.draw.rect(screen, (180, 150, 70), (300, 0, 80, HEIGHT))

    elif level["name"] == "Серая база":
        pygame.draw.rect(screen, level["accent"], (0, 0, WIDTH, 70))
        pygame.draw.rect(screen, level["accent"], (0, HEIGHT - 70, WIDTH, 70))
        pygame.draw.rect(screen, (80, 80, 100), (360, 160, 80, 280))
