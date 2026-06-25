# Игрок и связанные объекты: пули, монета, бонусное оружие, эффект подбора.
import random
import pygame

import config
from config import (
    ANIMATION_DELAY,
    BULLET_DAMAGE,
    BULLET_SPEED,
    COIN_EFFECT_FRAME_DELAY,
    HEIGHT,
    SHOT_DELAY,
    WEAPON_DURATION,
    WIDTH,
    advance_animation,
    create_animation_frames,
    create_bullet_image,
    create_coin_animation_frames,
    create_coin_collect_frames,
    create_coin_image,
    create_player_image,
    create_weapon_image,
    load_sprite_image,
)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        base_image = load_sprite_image(
            "player.png",
            (40, 40),
            create_player_image(40)
        )
        self.frames = create_animation_frames(base_image)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(50, 50))
        self.speed = 5
        self.health = 100
        self.direction_x = 1
        self.direction_y = 0
        self.last_shot_time = -SHOT_DELAY
        self.frame_index = 0
        self.last_frame_time = 0
        self.is_moving = False
        self.weapon_until = 0

    def reset_to_center(self):
        # В начале каждого раунда герой появляется в центре экрана.
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.is_moving = False

    def move(self):
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0

        if keys[pygame.K_w]:
            move_y -= 1

        if keys[pygame.K_s]:
            move_y += 1

        if keys[pygame.K_a]:
            move_x -= 1

        if keys[pygame.K_d]:
            move_x += 1

        if move_x != 0 or move_y != 0:
            self.direction_x = move_x
            self.direction_y = move_y
            self.is_moving = True
        else:
            self.is_moving = False

        self.rect.x += move_x * self.speed
        self.rect.y += move_y * self.speed

        self.rect.clamp_ip(config.screen.get_rect())

    def update_animation(self, current_time):
        center = self.rect.center

        if self.is_moving:
            self.frame_index, self.last_frame_time = advance_animation(
                self.frame_index,
                self.last_frame_time,
                current_time,
                ANIMATION_DELAY,
                len(self.frames)
            )
        else:
            self.frame_index = 0
            self.last_frame_time = current_time

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)
        self.rect.clamp_ip(config.screen.get_rect())

    def can_shoot(self, current_time):
        return current_time - self.last_shot_time >= SHOT_DELAY

    def has_power_weapon(self, current_time):
        return current_time < self.weapon_until

    def pick_up_weapon(self, current_time):
        self.weapon_until = current_time + WEAPON_DURATION

    def make_bullets(self, direction_x, direction_y, current_time):
        direction = pygame.math.Vector2(direction_x, direction_y)

        if direction.length() == 0:
            direction = pygame.math.Vector2(1, 0)

        direction = direction.normalize()

        if not self.has_power_weapon(current_time):
            return [
                Bullet(
                    self.rect.centerx,
                    self.rect.centery,
                    direction.x,
                    direction.y
                )
            ]

        # Усиленное оружие: тройной разлёт и удвоенный урон.
        bullets = []

        for angle in (-18, 0, 18):
            spread = direction.rotate(angle)
            bullet = Bullet(
                self.rect.centerx,
                self.rect.centery,
                spread.x,
                spread.y
            )
            bullet.damage = BULLET_DAMAGE * 2
            bullets.append(bullet)

        return bullets

    def shoot(self, current_time):
        if not self.can_shoot(current_time):
            return []

        self.last_shot_time = current_time
        return self.make_bullets(self.direction_x, self.direction_y, current_time)

    def shoot_at(self, target_position, current_time):
        if not self.can_shoot(current_time):
            return []

        target_x, target_y = target_position
        self.last_shot_time = current_time
        return self.make_bullets(
            target_x - self.rect.centerx,
            target_y - self.rect.centery,
            current_time
        )

    def draw(self):
        config.screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_x, direction_y):
        super().__init__()
        self.image = load_sprite_image(
            "bullet.png",
            (10, 10),
            create_bullet_image(10)
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y
        self.damage = BULLET_DAMAGE
        direction = pygame.math.Vector2(direction_x, direction_y)

        if direction.length() == 0:
            direction = pygame.math.Vector2(1, 0)

        self.velocity = direction.normalize() * BULLET_SPEED

    def update(self):
        # Храним точные координаты, чтобы диагональная стрельба не дёргалась.
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.rect.center = (round(self.x), round(self.y))

    def is_outside_screen(self):
        return not config.screen.get_rect().colliderect(self.rect)

    def draw(self):
        config.screen.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        base_image = load_sprite_image(
            "coin.png",
            (20, 20),
            create_coin_image(20)
        )
        self.frames = create_coin_animation_frames(base_image)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(
            topleft=(
                random.randint(50, 730),
                random.randint(50, 530)
            )
        )
        self.frame_index = 0
        self.last_frame_time = 0

    def update(self, current_time):
        center = self.rect.center
        self.frame_index, self.last_frame_time = advance_animation(
            self.frame_index,
            self.last_frame_time,
            current_time,
            ANIMATION_DELAY,
            len(self.frames)
        )
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)

    def draw(self):
        config.screen.blit(self.image, self.rect)


class WeaponPickup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        base_image = load_sprite_image(
            "weapon.png",
            (28, 28),
            create_weapon_image(28)
        )
        self.frames = create_animation_frames(base_image)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(
            center=(
                random.randint(60, WIDTH - 60),
                random.randint(80, HEIGHT - 60)
            )
        )
        self.frame_index = 0
        self.last_frame_time = 0

    def update(self, current_time):
        center = self.rect.center
        self.frame_index, self.last_frame_time = advance_animation(
            self.frame_index,
            self.last_frame_time,
            current_time,
            ANIMATION_DELAY,
            len(self.frames)
        )
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)

    def draw(self):
        config.screen.blit(self.image, self.rect)


class CoinCollectEffect(pygame.sprite.Sprite):
    def __init__(self, center, current_time):
        super().__init__()
        self.frames = create_coin_collect_frames()
        self.frame_index = 0
        self.last_frame_time = current_time
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)

    def update(self, current_time):
        if current_time - self.last_frame_time < COIN_EFFECT_FRAME_DELAY:
            return

        steps = (current_time - self.last_frame_time) // COIN_EFFECT_FRAME_DELAY
        self.frame_index += steps
        self.last_frame_time += steps * COIN_EFFECT_FRAME_DELAY

        if self.frame_index >= len(self.frames):
            self.kill()
            return

        center = self.rect.center
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)
