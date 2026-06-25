# Экраны конца игры: поражение и победа.
import sys
import pygame

from config import (
    BLACK,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    audio,
    big_font,
    draw_text,
    font,
    update_highscore,
)
import config


def game_over(score):
    high_score, is_new_record = update_highscore(score)
    audio.stop_music()
    audio.play_sound("game_over")

    while True:
        config.screen.fill(BLACK)

        draw_text(
            "ПОРАЖЕНИЕ",
            big_font,
            RED,
            220,
            180
        )

        draw_text(
            f"Очки: {score}",
            font,
            WHITE,
            330,
            300
        )

        draw_text(
            f"Рекорд: {high_score}",
            font,
            YELLOW,
            315,
            340
        )

        if is_new_record:
            draw_text(
                "Новый рекорд!",
                font,
                GREEN,
                300,
                380
            )

        draw_text(
            "ESC - выход",
            font,
            WHITE,
            300,
            430
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def victory(score):
    high_score, is_new_record = update_highscore(score)
    audio.stop_music()
    audio.play_sound("victory")

    while True:
        config.screen.fill(BLACK)

        draw_text(
            "ПОБЕДА!",
            big_font,
            GREEN,
            240,
            180
        )

        draw_text(
            f"Очки: {score}",
            font,
            WHITE,
            330,
            300
        )

        draw_text(
            f"Рекорд: {high_score}",
            font,
            YELLOW,
            315,
            340
        )

        if is_new_record:
            draw_text(
                "Новый рекорд!",
                font,
                GREEN,
                300,
                380
            )

        draw_text(
            "ESC - выход",
            font,
            WHITE,
            300,
            430
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
