import pygame
import sys
import random

pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 40, 40)
        self.speed = 5
        self.health = 100

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.rect.y -= self.speed

        if keys[pygame.K_s]:
            self.rect.y += self.speed

        if keys[pygame.K_a]:
            self.rect.x -= self.speed

        if keys[pygame.K_d]:
            self.rect.x += self.speed

        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)


class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(650, 450, 40, 40)
        self.speed = 2

    def update(self, player):
        if player.rect.x > self.rect.x:
            self.rect.x += self.speed

        if player.rect.x < self.rect.x:
            self.rect.x -= self.speed

        if player.rect.y > self.rect.y:
            self.rect.y += self.speed

        if player.rect.y < self.rect.y:
            self.rect.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


class Coin:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(50, 730),
            random.randint(50, 530),
            20,
            20
        )

    def draw(self):
        pygame.draw.rect(screen, YELLOW, self.rect)


def draw_text(text, current_font, color, x, y):
    image = current_font.render(text, True, color)
    screen.blit(image, (x, y))


def menu():
    while True:
        screen.fill(BLACK)

        draw_text(
            "Game demo",
            big_font,
            WHITE,
            180,
            180
        )

        draw_text(
            "ENTER - начать игру",
            font,
            WHITE,
            260,
            320
        )

        draw_text(
            "ESC - выход",
            font,
            WHITE,
            310,
            370
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def game_over(score):
    while True:
        screen.fill(BLACK)

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
            "ESC - выход",
            font,
            WHITE,
            300,
            370
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
    while True:
        screen.fill(BLACK)

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
            "ESC - выход",
            font,
            WHITE,
            300,
            370
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


def game():
    player = Player()
    enemy = Enemy()
    coin = Coin()

    score = 0

    start_time = pygame.time.get_ticks()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player.move()
        enemy.update(player)

        if player.rect.colliderect(enemy.rect):
            player.health -= 1

        if player.rect.colliderect(coin.rect):
            score += 1
            coin = Coin()

        elapsed_time = (
            pygame.time.get_ticks() - start_time
        ) // 1000

        if player.health <= 0:
            game_over(score)

        if score >= 10:
            victory(score)

        screen.fill(BLUE)

        player.draw()
        enemy.draw()
        coin.draw()

        draw_text(
            f"HP: {player.health}",
            font,
            WHITE,
            20,
            20
        )

        draw_text(
            f"Очки: {score}",
            font,
            WHITE,
            20,
            60
        )

        draw_text(
            f"Время: {elapsed_time}",
            font,
            WHITE,
            20,
            100
        )

        pygame.display.flip()


menu()
game()
