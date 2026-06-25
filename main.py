# Точка входа: связывает модули и содержит главный игровой цикл.
import random
import sys
import pygame

import config
from config import (
    CYAN,
    FPS,
    ROUND_DURATION,
    ROUND_PAUSE_TIME,
    WEAPON_SPAWN_MAX,
    WEAPON_SPAWN_MIN,
    WHITE,
    YELLOW,
    audio,
    clock,
    draw_text,
    font,
)
from game.player import Coin, CoinCollectEffect, Player, WeaponPickup
from game.enemy import create_enemies
from game.level import LEVELS, draw_level_background
from ui.menu import menu
from ui.screens import game_over, victory


def game():
    audio.play_music("game_music")

    player = Player()
    player.reset_to_center()
    player_group = pygame.sprite.Group(player)
    level_index = 0
    current_level = LEVELS[level_index]
    round_number = 1
    enemies = create_enemies(
        round_number,
        current_level,
        level_index + 1
    )
    bullets = pygame.sprite.Group()
    effects = pygame.sprite.Group()
    coin = Coin()
    coin_group = pygame.sprite.Group(coin)
    weapon_group = pygame.sprite.Group()

    score = 0

    start_time = pygame.time.get_ticks()
    round_start_time = start_time
    round_pause_until = start_time + ROUND_PAUSE_TIME
    is_round_pause = True
    last_player_hit_sound_time = 0

    # Бонусное оружие появляется один раз за локацию в случайный момент.
    weapon_spawned_this_level = False
    weapon_spawn_at = start_time + random.randint(WEAPON_SPAWN_MIN, WEAPON_SPAWN_MAX)

    while True:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        screen = config.screen

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not is_round_pause and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # SPACE стреляет в последнее направление движения игрока.
                    new_bullets = player.shoot(current_time)

                    if new_bullets:
                        bullets.add(*new_bullets)
                        audio.play_sound("attack")

            if not is_round_pause and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # ЛКМ стреляет в сторону курсора.
                    new_bullets = player.shoot_at(event.pos, current_time)

                    if new_bullets:
                        bullets.add(*new_bullets)
                        audio.play_sound("attack")

        if is_round_pause:
            player.is_moving = False

            if current_time >= round_pause_until:
                is_round_pause = False
                round_start_time = current_time
        else:
            player.move()

            for bullet in bullets.sprites():
                bullet.update()

                if bullet.is_outside_screen():
                    bullet.kill()
                    continue

                hit_enemies = pygame.sprite.spritecollide(
                    bullet,
                    enemies,
                    False
                )

                for enemy in hit_enemies:
                    # Попадание снимает здоровье; враг исчезает при нуле.
                    enemy.take_damage(bullet.damage, current_time)
                    bullet.kill()
                    audio.play_sound("hit")

                    if enemy.health <= 0:
                        enemy.kill()

                    break

            for enemy in enemies:
                enemy.update(player)

                if player.rect.colliderect(enemy.rect):
                    player.health -= enemy.damage

                    if current_time - last_player_hit_sound_time >= 400:
                        audio.play_sound("player_hit")
                        last_player_hit_sound_time = current_time

            if pygame.sprite.spritecollideany(player, coin_group):
                score += 1
                audio.play_sound("coin")
                effects.add(CoinCollectEffect(coin.rect.center, current_time))
                coin.kill()
                coin = Coin()
                coin_group.empty()
                coin_group.add(coin)

            # Появление бонусного оружия в случайный момент текущей локации.
            if (
                not weapon_spawned_this_level
                and len(weapon_group) == 0
                and current_time >= weapon_spawn_at
            ):
                weapon_group.add(WeaponPickup())
                weapon_spawned_this_level = True

            picked_weapon = pygame.sprite.spritecollideany(player, weapon_group)

            if picked_weapon is not None:
                player.pick_up_weapon(current_time)
                audio.play_sound("weapon")
                effects.add(CoinCollectEffect(picked_weapon.rect.center, current_time))
                weapon_group.empty()

            round_time_is_over = (
                current_time - round_start_time >= ROUND_DURATION * 1000
            )

            # Раунд заканчивается по таймеру или когда все враги уничтожены.
            if round_time_is_over or len(enemies) == 0:
                bullets.empty()
                effects.empty()

                if round_number >= current_level["rounds"]:
                    level_index += 1

                    if level_index >= len(LEVELS):
                        victory(score)

                    current_level = LEVELS[level_index]
                    round_number = 1
                    coin = Coin()
                    coin_group.empty()
                    coin_group.add(coin)

                    # Новая локация - новое случайное появление оружия.
                    weapon_group.empty()
                    weapon_spawned_this_level = False
                    weapon_spawn_at = current_time + random.randint(
                        WEAPON_SPAWN_MIN,
                        WEAPON_SPAWN_MAX
                    )
                else:
                    round_number += 1

                # В начале нового раунда возвращаем героя в центр экрана.
                player.reset_to_center()

                enemies = create_enemies(
                    round_number,
                    current_level,
                    level_index + 1
                )
                round_pause_until = current_time + ROUND_PAUSE_TIME
                is_round_pause = True

        if player.health <= 0:
            game_over(score)

        player.update_animation(current_time)

        for enemy in enemies:
            enemy.update_animation(current_time)

        coin_group.update(current_time)
        weapon_group.update(current_time)
        effects.update(current_time)

        draw_level_background(current_level)

        player_group.draw(screen)
        enemies.draw(screen)

        for enemy in enemies:
            enemy.draw_health_bar(screen)

        bullets.draw(screen)
        coin_group.draw(screen)
        weapon_group.draw(screen)
        effects.draw(screen)

        draw_text(
            f"HP: {player.health}",
            font,
            WHITE,
            20,
            20
        )

        draw_text(
            f"Уровень: {level_index + 1}/{len(LEVELS)}",
            font,
            WHITE,
            20,
            60
        )

        draw_text(
            f"Раунд: {round_number}/{current_level['rounds']}",
            font,
            WHITE,
            20,
            100
        )

        if player.has_power_weapon(current_time):
            weapon_seconds = (player.weapon_until - current_time) // 1000 + 1
            draw_text(
                f"Оружие: {weapon_seconds}с",
                font,
                CYAN,
                20,
                140
            )

        if is_round_pause:
            draw_text(
                f"Уровень {level_index + 1}",
                font,
                WHITE,
                330,
                220
            )

            draw_text(
                f"Раунд {round_number}",
                config.big_font,
                WHITE,
                280,
                260
            )

        if config.show_fps_enabled:
            draw_text(
                f"FPS: {int(clock.get_fps())}",
                font,ыOW,
                config.WIDTH - 150,
                20
            )

        pygame.display.flip()


if __name__ == "__main__":
    menu()
    game()
