# Главное меню и экраны настроек (звук, управление, видео).
import sys
import pygame

import config
from config import (
    BLACK,
    GRAY,
    GREEN,
    HEIGHT,
    WHITE,
    WIDTH,
    YELLOW,
    audio,
    big_font,
    font,
    load_highscore,
)


class MenuItem:
    def __init__(self, label, on_activate=None, on_adjust=None,
                 get_value=None, on_set=None):
        # label может быть строкой или функцией без аргументов (динамический текст).
        # get_value/on_set превращают пункт в ползунок (значение 0..1).
        self.label = label
        self.on_activate = on_activate
        self.on_adjust = on_adjust
        self.get_value = get_value
        self.on_set = on_set

    @property
    def is_slider(self):
        return self.get_value is not None

    @property
    def selectable(self):
        return (
            self.on_activate is not None
            or self.on_adjust is not None
            or self.on_set is not None
        )

    def get_text(self):
        return self.label() if callable(self.label) else self.label

    def activate(self):
        if self.on_activate is not None:
            return self.on_activate()
        return None

    def adjust(self, delta):
        if self.on_adjust is not None:
            self.on_adjust(delta)


def run_menu(title, items, escape_value=None):
    # Универсальное меню: работает и мышью, и клавиатурой.
    selectable = [index for index, item in enumerate(items) if item.selectable]
    cursor = 0

    button_width = 480
    button_height = 52
    gap = 14

    while True:
        screen = config.screen
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BLACK)

        title_image = big_font.render(title, True, WHITE)
        screen.blit(title_image, title_image.get_rect(center=(WIDTH // 2, 110)))

        rects = []
        slider_tracks = {}
        y = 200

        for index, item in enumerate(items):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (WIDTH // 2, y + button_height // 2)
            rects.append(rect)

            if not item.selectable:
                # Информационная строка без рамки.
                text_image = font.render(item.get_text(), True, GRAY)
                screen.blit(text_image, text_image.get_rect(center=rect.center))
                y += button_height + gap
                continue

            is_active = (
                selectable[cursor] == index
                or rect.collidepoint(mouse_pos)
            )
            background = (70, 70, 110) if is_active else (40, 40, 60)
            border = YELLOW if is_active else GRAY

            pygame.draw.rect(screen, background, rect, border_radius=10)
            pygame.draw.rect(screen, border, rect, 2, border_radius=10)

            text_image = font.render(item.get_text(), True, WHITE)

            if item.is_slider:
                # Текст слева, ползунок справа.
                screen.blit(
                    text_image,
                    text_image.get_rect(midleft=(rect.left + 18, rect.centery))
                )

                track = pygame.Rect(rect.right - 190, rect.centery - 4, 160, 8)
                slider_tracks[index] = track
                fraction = max(0.0, min(1.0, item.get_value()))
                fill = pygame.Rect(
                    track.left,
                    track.top,
                    int(track.width * fraction),
                    track.height
                )
                knob_x = track.left + int(track.width * fraction)

                pygame.draw.rect(screen, (30, 30, 45), track, border_radius=4)
                pygame.draw.rect(screen, GREEN, fill, border_radius=4)
                pygame.draw.circle(screen, WHITE, (knob_x, track.centery), 9)
                pygame.draw.circle(screen, YELLOW, (knob_x, track.centery), 9, 2)
            else:
                screen.blit(text_image, text_image.get_rect(center=rect.center))

            y += button_height + gap

        hint_image = font.render(
            "Стрелки - выбор, Enter - применить, Esc - назад",
            True,
            GRAY
        )
        screen.blit(hint_image, hint_image.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                for position, index in enumerate(selectable):
                    if rects[index].collidepoint(event.pos):
                        cursor = position

                # Перетаскивание ползунка зажатой ЛКМ.
                if event.buttons[0]:
                    index = selectable[cursor]

                    if index in slider_tracks:
                        track = slider_tracks[index]
                        fraction = (event.pos[0] - track.left) / track.width
                        items[index].on_set(max(0.0, min(1.0, fraction)))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for position, index in enumerate(selectable):
                    if not rects[index].collidepoint(event.pos):
                        continue

                    cursor = position

                    if index in slider_tracks:
                        track = slider_tracks[index]
                        fraction = (event.pos[0] - track.left) / track.width
                        items[index].on_set(max(0.0, min(1.0, fraction)))
                        break

                    result = items[index].activate()

                    if result is not None:
                        return result

                    break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return escape_value

                if event.key in (pygame.K_UP, pygame.K_w):
                    cursor = (cursor - 1) % len(selectable)

                if event.key in (pygame.K_DOWN, pygame.K_s):
                    cursor = (cursor + 1) % len(selectable)

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    result = items[selectable[cursor]].activate()

                    if result is not None:
                        return result

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    items[selectable[cursor]].adjust(-1)

                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    items[selectable[cursor]].adjust(1)


def audio_settings_menu():
    def music_label():
        if audio.music_muted:
            return "Музыка: выкл"
        return f"Музыка: {int(round(audio.music_volume * 100))}%"

    def sounds_label():
        if audio.sounds_muted:
            return "Звуки: выкл"
        return f"Звуки: {int(round(audio.sound_volume * 100))}%"

    def music_value():
        return 0.0 if audio.music_muted else audio.music_volume

    def sounds_value():
        return 0.0 if audio.sounds_muted else audio.sound_volume

    def adjust_music(delta):
        audio.music_muted = False
        audio.set_music_volume(audio.music_volume + delta * 0.1)

    def set_music(fraction):
        audio.music_muted = False
        audio.set_music_volume(fraction)

    def adjust_sounds(delta):
        audio.sounds_muted = False
        audio.set_sound_volume(audio.sound_volume + delta * 0.1)
        audio.play_sound("coin")

    def set_sounds(fraction):
        audio.sounds_muted = False
        audio.set_sound_volume(fraction)
        audio.play_sound("coin")

    def toggle_sounds():
        audio.toggle_sounds_muted()
        audio.play_sound("coin")

    items = [
        MenuItem("Ползунок: мышь или стрелки, Enter - вкл/выкл"),
        MenuItem(
            music_label,
            on_activate=audio.toggle_music_muted,
            on_adjust=adjust_music,
            get_value=music_value,
            on_set=set_music
        ),
        MenuItem(
            sounds_label,
            on_activate=toggle_sounds,
            on_adjust=adjust_sounds,
            get_value=sounds_value,
            on_set=set_sounds
        ),
        MenuItem("Назад", on_activate=lambda: "back"),
    ]
    run_menu("Музыка и звуки", items, escape_value="back")


def controls_settings_menu():
    items = [
        MenuItem("W / A / S / D - движение"),
        MenuItem("SPACE - выстрел по направлению"),
        MenuItem("ЛКМ - выстрел в сторону курсора"),
        MenuItem("ESC - выход / назад"),
        MenuItem("Назад", on_activate=lambda: "back"),
    ]
    run_menu("Управление", items, escape_value="back")


def video_settings_menu():
    def fullscreen_label():
        return f"Полный экран: {'вкл' if config.fullscreen_enabled else 'выкл'}"

    def fps_label():
        return f"Счётчик FPS: {'вкл' if config.show_fps_enabled else 'выкл'}"

    def toggle_fullscreen():
        config.set_fullscreen(not config.fullscreen_enabled)

    def toggle_fps():
        config.show_fps_enabled = not config.show_fps_enabled

    items = [
        MenuItem(fullscreen_label, on_activate=toggle_fullscreen),
        MenuItem(fps_label, on_activate=toggle_fps),
        MenuItem("Назад", on_activate=lambda: "back"),
    ]
    run_menu("Видео", items, escape_value="back")


def settings_menu():
    items = [
        MenuItem("Музыка и звуки", on_activate=audio_settings_menu),
        MenuItem("Управление", on_activate=controls_settings_menu),
        MenuItem("Видео", on_activate=video_settings_menu),
        MenuItem("Назад", on_activate=lambda: "back"),
    ]
    run_menu("Настройки", items, escape_value="back")


def menu():
    high_score = load_highscore()
    audio.play_music("menu_music")

    items = [
        MenuItem(f"Рекорд: {high_score}"),
        MenuItem("Играть", on_activate=lambda: "play"),
        MenuItem("Настройки", on_activate=settings_menu),
        MenuItem("Выход", on_activate=lambda: "quit"),
    ]

    result = run_menu("Game demo", items, escape_value="quit")

    if result == "quit":
        pygame.quit()
        sys.exit()

    audio.play_music("game_music")
