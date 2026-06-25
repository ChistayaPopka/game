# Общий код игры: настройки, экран, шрифты, цвета, помощники и звук.
# Модули game/ и ui/ импортируют отсюда, поэтому config ничего из них не импортирует.
import pygame
import os
import json
import math
from array import array

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60
ROUND_DURATION = 15
ROUND_PAUSE_TIME = 2000
BULLET_SPEED = 9
BULLET_DAMAGE = 2
SHOT_DELAY = 300
ANIMATION_DELAY = 120
HIT_FLASH_TIME = 120
COIN_EFFECT_FRAME_DELAY = 70
WEAPON_DURATION = 8000
WEAPON_SPAWN_MIN = 5000
WEAPON_SPAWN_MAX = 15000
HIGH_SCORE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "highscore.json"
)
ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets"
)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 150, 0)
PURPLE = (130, 0, 180)
CYAN = (0, 220, 220)
LIGHT_GREEN = (70, 180, 90)
SAND = (210, 180, 90)
GRAY = (100, 100, 120)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Параметры дисплея, общие для меню и игрового цикла.
fullscreen_enabled = False
show_fps_enabled = False


def set_fullscreen(enabled):
    # Переключение полноэкранного режима без падения, если драйвер его не даёт.
    global screen, fullscreen_enabled

    try:
        if enabled:
            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.FULLSCREEN | pygame.SCALED
            )
        else:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))

        fullscreen_enabled = enabled
    except pygame.error:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        fullscreen_enabled = False


def load_sprite_image(filename, size, fallback_image):
    # Спрайт можно заменить файлом из папки assets, но без файла игра не падает.
    path = os.path.join(ASSETS_DIR, filename)

    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except (pygame.error, FileNotFoundError, OSError):
        return fallback_image


background_cache = {}


def load_background_image(filename):
    if filename in background_cache:
        return background_cache[filename]

    path = os.path.join(ASSETS_DIR, filename)

    try:
        image = pygame.image.load(path).convert()
        image = pygame.transform.scale(image, (WIDTH, HEIGHT))
    except (pygame.error, FileNotFoundError, OSError):
        image = None

    background_cache[filename] = image
    return image


def create_player_image(size):
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(image, GREEN, (size // 2, size // 2), size // 2)
    pygame.draw.circle(image, WHITE, (size // 2 + 7, size // 2 - 5), 5)
    pygame.draw.polygon(
        image,
        (20, 120, 20),
        [(size // 2, 4), (size - 6, size // 2), (size // 2, size - 4)]
    )
    return image


def create_enemy_image(size, color):
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(image, color, (3, 3, size - 6, size - 6), border_radius=8)
    pygame.draw.rect(image, BLACK, (size // 4, size // 4, 6, 6))
    pygame.draw.rect(image, BLACK, (size - size // 4 - 6, size // 4, 6, 6))
    pygame.draw.line(
        image,
        BLACK,
        (size // 4, size - size // 4),
        (size - size // 4, size - size // 4),
        3
    )
    return image


def create_coin_image(size):
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(image, YELLOW, (size // 2, size // 2), size // 2)
    pygame.draw.circle(image, (220, 160, 0), (size // 2, size // 2), size // 3, 2)
    return image


def create_bullet_image(size):
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(image, WHITE, (size // 2, size // 2), size // 2)
    pygame.draw.circle(image, YELLOW, (size // 2, size // 2), size // 3)
    return image


def create_weapon_image(size):
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.polygon(
        image,
        CYAN,
        [(size // 2, 2), (size - 2, size // 2), (size // 2, size - 2), (2, size // 2)]
    )
    pygame.draw.polygon(
        image,
        WHITE,
        [(size // 2, 2), (size - 2, size // 2), (size // 2, size - 2), (2, size // 2)],
        2
    )
    pygame.draw.line(image, WHITE, (size // 2, 8), (size // 2, size - 8), 3)
    pygame.draw.line(image, WHITE, (8, size // 2), (size - 8, size // 2), 3)
    return image


def scale_image_keep_size(image, scale_x, scale_y):
    width, height = image.get_size()
    scaled_width = max(1, round(width * scale_x))
    scaled_height = max(1, round(height * scale_y))
    scaled_image = pygame.transform.smoothscale(
        image,
        (scaled_width, scaled_height)
    )
    frame = pygame.Surface((width, height), pygame.SRCALPHA)
    frame.blit(
        scaled_image,
        scaled_image.get_rect(center=(width // 2, height // 2))
    )
    return frame


def create_animation_frames(base_image):
    # Кадры строятся из одного спрайта, поэтому отдельный sprite sheet не нужен.
    return [
        base_image.copy(),
        scale_image_keep_size(base_image, 1.08, 0.95),
        base_image.copy(),
        scale_image_keep_size(base_image, 0.95, 1.08)
    ]


def create_coin_animation_frames(base_image):
    return [
        base_image.copy(),
        scale_image_keep_size(base_image, 0.75, 1.0),
        scale_image_keep_size(base_image, 0.45, 1.0),
        scale_image_keep_size(base_image, 0.75, 1.0)
    ]


def create_flash_image(base_image):
    flash_image = base_image.copy()
    flash_image.fill((120, 120, 120, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return flash_image


def advance_animation(frame_index, last_frame_time, current_time, delay, frame_count):
    # Анимация зависит от времени, а не от количества отрисованных кадров.
    if current_time - last_frame_time >= delay:
        steps = (current_time - last_frame_time) // delay
        frame_index = (frame_index + steps) % frame_count
        last_frame_time += steps * delay

    return frame_index, last_frame_time


def create_coin_collect_frames():
    frames = []

    for index in range(6):
        size = 56
        image = pygame.Surface((size, size), pygame.SRCALPHA)
        alpha = max(0, 230 - index * 35)
        radius = 8 + index * 4
        pygame.draw.circle(
            image,
            (255, 230, 0, alpha),
            (size // 2, size // 2),
            radius,
            3
        )
        pygame.draw.circle(
            image,
            (255, 255, 255, alpha),
            (size // 2, size // 2),
            max(2, 6 - index)
        )
        frames.append(image)

    return frames


def draw_text(text, current_font, color, x, y):
    image = current_font.render(text, True, color)
    screen.blit(image, (x, y))


class AudioManager:
    AUDIO_EXTENSIONS = [".ogg", ".wav", ".mp3"]
    AUDIO_ALIASES = {
        "attack": ["attack", "shoot", "sound_attack"],
        "coin": ["coin", "pickup", "sound_coin"],
        "weapon": ["weapon", "powerup", "sound_weapon"],
        "hit": ["hit", "enemy_hit", "sound_hit"],
        "player_hit": ["player_hit", "damage", "hurt", "sound_player_hit"],
        "game_over": ["game_over", "lose", "defeat", "sound_game_over"],
        "victory": ["victory", "win", "sound_victory"],
        "menu_music": ["menu_music", "music_menu"],
        "game_music": ["game_music", "music_game"]
    }

    def __init__(self):
        self.enabled = False
        self.music_channel = None
        self.current_music = None
        self.sounds = {}
        self.music_volume = 0.35
        self.sound_volume = 0.8
        self.music_muted = False
        self.sounds_muted = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)

            pygame.mixer.set_num_channels(12)
            self.music_channel = pygame.mixer.Channel(0)
            self.enabled = True
            self.create_sounds()
        except (pygame.error, TypeError, ValueError):
            # Без аудиоустройства игра должна работать молча, без падения.
            self.enabled = False

    def create_sounds(self):
        fallback_sounds = {
            "attack": self.create_tone(760, 80, 0.25),
            "coin": self.create_sequence([(880, 70), (1175, 90)], 0.35),
            "weapon": self.create_sequence([(659, 70), (880, 70), (1175, 130)], 0.35),
            "hit": self.create_sequence([(180, 70), (120, 90)], 0.35),
            "player_hit": self.create_sequence([(140, 120), (90, 120)], 0.35),
            "game_over": self.create_sequence([(220, 180), (165, 220), (110, 320)], 0.35),
            "victory": self.create_sequence([(523, 140), (659, 140), (784, 260)], 0.35),
            "menu_music": self.create_sequence(
                [(330, 240), (392, 240), (494, 240), (392, 240)],
                0.12
            ),
            "game_music": self.create_sequence(
                [(220, 160), (277, 160), (330, 160), (277, 160), (196, 240)],
                0.10
            )
        }

        for name, fallback_sound in fallback_sounds.items():
            self.sounds[name] = self.load_audio_from_assets(name, fallback_sound)

    def load_audio_from_assets(self, name, fallback_sound):
        # Сначала ищем пользовательский звук в assets, затем используем fallback.
        for path in self.get_audio_paths(name):
            try:
                return pygame.mixer.Sound(path)
            except (pygame.error, FileNotFoundError, OSError):
                pass

        return fallback_sound

    def get_audio_paths(self, name):
        aliases = self.AUDIO_ALIASES.get(name, [name])
        folders = [
            ASSETS_DIR,
            os.path.join(ASSETS_DIR, "sounds")
        ]

        for folder in folders:
            for alias in aliases:
                for extension in self.AUDIO_EXTENSIONS:
                    yield os.path.join(folder, alias + extension)

    def create_tone(self, frequency, duration_ms, volume):
        return self.create_sequence([(frequency, duration_ms)], volume)

    def create_sequence(self, notes, volume):
        mixer_info = pygame.mixer.get_init()

        if not self.enabled or mixer_info is None:
            return None

        frequency, sound_format, channels = mixer_info
        samples = array("h")

        for note_frequency, duration_ms in notes:
            sample_count = int(frequency * duration_ms / 1000)

            for index in range(sample_count):
                progress = index / max(1, sample_count - 1)
                fade = min(1.0, progress * 8, (1.0 - progress) * 8)
                value = int(
                    math.sin(2 * math.pi * note_frequency * index / frequency)
                    * 32767
                    * volume
                    * fade
                )

                for _ in range(channels):
                    samples.append(value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play_sound(self, name):
        if not self.enabled or self.sounds_muted:
            return

        sound = self.sounds.get(name)

        if sound is not None:
            sound.set_volume(self.sound_volume)
            sound.play()

    def effective_music_volume(self):
        return 0.0 if self.music_muted else self.music_volume

    def play_music(self, name):
        if not self.enabled or self.current_music == name:
            return

        sound = self.sounds.get(name)

        if sound is None:
            return

        self.music_channel.stop()
        self.music_channel.set_volume(self.effective_music_volume())
        self.music_channel.play(sound, loops=-1)
        self.current_music = name

    def stop_music(self):
        if not self.enabled:
            return

        self.music_channel.stop()
        self.current_music = None

    def set_music_volume(self, value):
        self.music_volume = max(0.0, min(1.0, round(value, 2)))

        if self.enabled and not self.music_muted:
            self.music_channel.set_volume(self.music_volume)

    def set_sound_volume(self, value):
        self.sound_volume = max(0.0, min(1.0, round(value, 2)))

    def toggle_music_muted(self):
        self.music_muted = not self.music_muted

        if self.enabled:
            self.music_channel.set_volume(self.effective_music_volume())

    def toggle_sounds_muted(self):
        self.sounds_muted = not self.sounds_muted


audio = AudioManager()


def load_highscore():
    # Если файла рекорда ещё нет или он повреждён, начинаем с нуля.
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return int(data.get("high_score", 0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_highscore(high_score):
    # Ошибки записи не должны ломать игру.
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
            json.dump(
                {"high_score": high_score},
                file,
                ensure_ascii=False,
                indent=4
            )
    except OSError:
        pass


def update_highscore(score):
    high_score = load_highscore()

    if score > high_score:
        save_highscore(score)
        return score, True

    return high_score, False
