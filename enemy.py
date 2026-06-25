# Враги: базовый класс, разновидности и фабрика отряда на раунд.
import random
import pygame

import config
from config import (
    ANIMATION_DELAY,
    BLACK,
    CYAN,
    GREEN,
    HEIGHT,
    HIT_FLASH_TIME,
    ORANGE,
    PURPLE,
    RED,
    WIDTH,
    YELLOW,
    advance_animation,
    create_animation_frames,
    create_enemy_image,
    create_flash_image,
    load_sprite_image,
)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed, color, damage, health, image_name):
        super().__init__()
        base_image = load_sprite_image(
            image_name,
            (size, size),
            create_enemy_image(size, color)
        )
        self.frames = create_animation_frames(base_image)
        self.flash_image = create_flash_image(base_image)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.color = color
        self.damage = damage
        self.health = health
        self.max_health = health
        self.frame_index = 0
        self.last_frame_time = 0
        self.flash_until = 0

    def update(self, player):
        # Базовое поведение: враг медленно преследует игрока.
        if player.rect.x > self.rect.x:
            self.rect.x += self.speed

        if player.rect.x < self.rect.x:
            self.rect.x -= self.speed

        if player.rect.y > self.rect.y:
            self.rect.y += self.speed

        if player.rect.y < self.rect.y:
            self.rect.y -= self.speed

    def take_damage(self, damage, current_time):
        self.health -= damage
        self.flash_until = current_time + HIT_FLASH_TIME

    def update_animation(self, current_time):
        center = self.rect.center

        if current_time < self.flash_until:
            self.image = self.flash_image
        else:
            self.frame_index, self.last_frame_time = advance_animation(
                self.frame_index,
                self.last_frame_time,
                current_time,
                ANIMATION_DELAY,
                len(self.frames)
            )
            self.image = self.frames[self.frame_index]

        self.rect = self.image.get_rect(center=center)

    def draw_health_bar(self, surface):
        # Полоска здоровья над врагом: зелёная -> жёлтая -> красная.
        if self.max_health <= 0:
            return

        fraction = max(0.0, min(1.0, self.health / self.max_health))
        bar_width = self.rect.width
        bar_height = 5
        x = self.rect.left
        y = self.rect.top - 9

        if fraction > 0.5:
            fill_color = GREEN
        elif fraction > 0.25:
            fill_color = YELLOW
        else:
            fill_color = RED

        background = pygame.Rect(x, y, bar_width, bar_height)
        fill = pygame.Rect(x, y, int(bar_width * fraction), bar_height)

        pygame.draw.rect(surface, (50, 0, 0), background)
        pygame.draw.rect(surface, fill_color, fill)
        pygame.draw.rect(surface, BLACK, background, 1)

    def draw(self):
        config.screen.blit(self.image, self.rect)


class NormalEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 2, RED, 1, 2, "enemy_normal.png")


class FastEnemy(Enemy):
    def __init__(self, x, y):
        # Быстрый враг меньше и слабее, зато быстрее догоняет игрока.
        super().__init__(x, y, 30, 3, ORANGE, 1, 1, "enemy_fast.png")


class TankEnemy(Enemy):
    def __init__(self, x, y):
        # Танк медленный, но крупный и наносит больше урона при столкновении.
        super().__init__(x, y, 55, 1, PURPLE, 3, 5, "enemy_tank.png")


class RandomEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 35, 3, CYAN, 1, 2, "enemy_random.png")
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.change_direction_time = 0

    def update(self, player):
        # Этот враг не преследует игрока напрямую: он меняет направление сам.
        current_time = pygame.time.get_ticks()

        if current_time >= self.change_direction_time:
            self.direction_x = random.choice([-1, 0, 1])
            self.direction_y = random.choice([-1, 0, 1])

            if self.direction_x == 0 and self.direction_y == 0:
                self.direction_x = 1

            self.change_direction_time = current_time + random.randint(700, 1400)

        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed

        game_area = config.screen.get_rect()

        if self.rect.left <= game_area.left or self.rect.right >= game_area.right:
            self.direction_x *= -1

        if self.rect.top <= game_area.top or self.rect.bottom >= game_area.bottom:
            self.direction_y *= -1

        self.rect.clamp_ip(game_area)


def get_random_spawn_position():
    # Враги появляются у краёв экрана, чтобы не возникать прямо внутри игрока.
    side = random.choice(["top", "right", "bottom", "left"])

    if side == "top":
        return random.randint(80, WIDTH - 80), 20

    if side == "right":
        return WIDTH - 80, random.randint(80, HEIGHT - 80)

    if side == "bottom":
        return random.randint(80, WIDTH - 80), HEIGHT - 80

    return 20, random.randint(80, HEIGHT - 80)


def strengthen_enemy(enemy, round_number, level_number):
    # С каждым раундом враги становятся опаснее.
    round_bonus = round_number + level_number - 2
    enemy.health += round_bonus
    enemy.max_health = enemy.health
    enemy.damage += round_bonus // 2
    enemy.speed += round_bonus // 3


def create_enemies(round_number, level, level_number):
    enemies = pygame.sprite.Group()
    enemy_count = 2 + round_number + level_number
    enemy_classes = level["enemy_classes"]

    for index in range(enemy_count):
        enemy_class = enemy_classes[index % len(enemy_classes)]
        x, y = get_random_spawn_position()
        enemy = enemy_class(x, y)
        strengthen_enemy(enemy, round_number, level_number)
        enemies.add(enemy)

    return enemies
