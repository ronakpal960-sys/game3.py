
import pygame
import random
import sys
import math
import os

pygame.init()

# ---------------- WINDOW ----------------
WIDTH, HEIGHT = 840, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON SNAKE | Arcade")

clock = pygame.time.Clock()

# ---------------- COLORS ----------------
BG = (9, 13, 25)
PANEL = (17, 25, 43)
GREEN = (40, 255, 150)
DARK_GREEN = (15, 180, 100)
RED = (255, 65, 100)
WHITE = (240, 245, 255)
GREY = (130, 145, 170)
BLUE = (65, 130, 255)
YELLOW = (255, 210, 80)

# ---------------- FONTS ----------------
title_font = pygame.font.SysFont("Arial", 52, bold=True)
big_font = pygame.font.SysFont("Arial", 38, bold=True)
font = pygame.font.SysFont("Arial", 23, bold=True)
small_font = pygame.font.SysFont("Arial", 17)

# ---------------- GAME SETTINGS ----------------
CELL = 20
BOARD_X = 20
BOARD_Y = 120
BOARD_W = 800
BOARD_H = 520

COLS = BOARD_W // CELL
ROWS = BOARD_H // CELL

# ---------------- HIGH SCORE ----------------
FILE = "best_score.txt"

try:
    with open(FILE, "r") as f:
        best_score = int(f.read())
except:
    best_score = 0


def save_best():
    with open(FILE, "w") as f:
        f.write(str(best_score))


# ---------------- BUTTON ----------------
class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self):
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)

        color = tuple(min(255, c + 35) for c in self.color) if hover else self.color

        pygame.draw.rect(screen, color, self.rect, border_radius=14)

        label = font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ---------------- BUTTONS ----------------
play_button = Button(310, 390, 220, 65, "PLAY GAME", (20, 155, 105))
resume_button = Button(310, 390, 220, 65, "RESUME", (20, 155, 105))
restart_button = Button(310, 475, 220, 60, "PLAY AGAIN", (40, 100, 190))
menu_button = Button(310, 555, 220, 55, "MAIN MENU", (65, 75, 100))


# ---------------- GAME VARIABLES ----------------
state = "MENU"

snake = []
food = (0, 0)
direction = (1, 0)
next_direction = (1, 0)

score = 0
speed = 9
move_timer = 0


def new_food():
    while True:
        position = (
            random.randrange(COLS),
            random.randrange(ROWS)
        )
        if position not in snake:
            return position


def reset_game():
    global snake, food, direction, next_direction
    global score, speed, move_timer

    snake = [(10, 12), (9, 12), (8, 12)]
    direction = (1, 0)
    next_direction = (1, 0)

    score = 0
    speed = 9
    move_timer = 0

    food = new_food()


# ---------------- DRAW FUNCTIONS ----------------
def draw_background():
    screen.fill(BG)

    # Decorative circles
    pygame.draw.circle(screen, (17, 32, 48), (0, 0), 180)
    pygame.draw.circle(screen, (20, 25, 55), (840, 680), 220)


def draw_text(text, font_obj, color, x, y):
    image = font_obj.render(text, True, color)
    screen.blit(image, image.get_rect(center=(x, y)))


def draw_board():
    board = pygame.Rect(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)

    pygame.draw.rect(screen, (12, 20, 34), board, border_radius=16)
    pygame.draw.rect(screen, (35, 60, 75), board, 2, border_radius=16)

    # Grid
    for x in range(BOARD_X, BOARD_X + BOARD_W, CELL):
        pygame.draw.line(
            screen, (21, 33, 48),
            (x, BOARD_Y),
            (x, BOARD_Y + BOARD_H)
        )

    for y in range(BOARD_Y, BOARD_Y + BOARD_H, CELL):
        pygame.draw.line(
            screen, (21, 33, 48),
            (BOARD_X, y),
            (BOARD_X + BOARD_W, y)
        )


def draw_snake():
    for i, part in enumerate(snake):

        x = BOARD_X + part[0] * CELL
        y = BOARD_Y + part[1] * CELL

        rect = pygame.Rect(x + 2, y + 2, CELL - 4, CELL - 4)

        if i == 0:
            # Snake head glow
            pygame.draw.rect(
                screen, (20, 100, 75),
                rect.inflate(8, 8),
                border_radius=8
            )

            pygame.draw.rect(
                screen, GREEN,
                rect,
                border_radius=7
            )

            # Eyes
            if direction == (1, 0):
                eyes = [(x + 14, y + 6), (x + 14, y + 14)]
            elif direction == (-1, 0):
                eyes = [(x + 6, y + 6), (x + 6, y + 14)]
            elif direction == (0, -1):
                eyes = [(x + 6, y + 6), (x + 14, y + 6)]
            else:
                eyes = [(x + 6, y + 14), (x + 14, y + 14)]

            for eye in eyes:
                pygame.draw.circle(screen, WHITE, eye, 2)

        else:
            pygame.draw.rect(
                screen,
                DARK_GREEN,
                rect,
                border_radius=6
            )


def draw_food():
    x = BOARD_X + food[0] * CELL + CELL // 2
    y = BOARD_Y + food[1] * CELL + CELL // 2

    # Glow effect
    pygame.draw.circle(screen, (100, 25, 55), (x, y), 13)
    pygame.draw.circle(screen, RED, (x, y), 8)
    pygame.draw.circle(screen, (255, 200, 200), (x - 2, y - 2), 3)


def draw_top_panel():
    pygame.draw.rect(
        screen, PANEL,
        (20, 15, 800, 85),
        border_radius=16
    )

    draw_text("NEON SNAKE", title_font, GREEN, 185, 55)

    draw_text("SCORE", small_font, GREY, 540, 37)
    draw_text(str(score), big_font, WHITE, 540, 69)

    draw_text("BEST", small_font, GREY, 700, 37)
    draw_text(str(best_score), big_font, YELLOW, 700, 69)


def draw_menu():
    draw_background()
    draw_top_panel()

    draw_text("THE CLASSIC ARCADE GAME", font, WHITE, 420, 190)

    draw_text("EAT  •  GROW  •  SURVIVE", big_font, GREEN, 420, 265)

    draw_text("Collect the red food and grow your snake.", small_font, GREY, 420, 315)

    play_button.draw()

    draw_text("Use ARROW KEYS to move", small_font, GREY, 420, 490)
    draw_text("P = Pause     ESC = Main Menu", small_font, GREY, 420, 525)


def draw_game():
    draw_background()
    draw_top_panel()
    draw_board()
    draw_food()
    draw_snake()

    draw_text(
        f"SPEED: {speed}",
        small_font,
        BLUE,
        420,
        655
    )


def draw_pause():
    draw_game()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))

    draw_text("GAME PAUSED", big_font, WHITE, 420, 285)
    draw_text("Take a break!", font, GREEN, 420, 335)

    resume_button.draw()
    menu_button.draw()


def draw_game_over():
    draw_game()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    screen.blit(overlay, (0, 0))

    draw_text("GAME OVER", title_font, RED, 420, 270)
    draw_text(f"YOUR SCORE: {score}", big_font, WHITE, 420, 340)

    restart_button.draw()
    menu_button.draw()


# ---------------- MAIN LOOP ----------------
reset_game()

while True:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                state = "MENU"

            if state == "PLAYING":

                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)

                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)

                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)

                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)

                elif event.key == pygame.K_p:
                    state = "PAUSED"

            elif state == "PAUSED":
                if event.key == pygame.K_p:
                    state = "PLAYING"

            elif state == "GAME_OVER":
                if event.key == pygame.K_SPACE:
                    reset_game()
                    state = "PLAYING"

        if state == "MENU" and play_button.clicked(event):
            reset_game()
            state = "PLAYING"

        elif state == "PAUSED":
            if resume_button.clicked(event):
                state = "PLAYING"
            elif menu_button.clicked(event):
                state = "MENU"

        elif state == "GAME_OVER":
            if restart_button.clicked(event):
                reset_game()
                state = "PLAYING"
            elif menu_button.clicked(event):
                state = "MENU"

    # ---------------- SNAKE MOVEMENT ----------------
    if state == "PLAYING":

        move_timer += dt

        if move_timer >= 1 / speed:
            move_timer = 0

            direction = next_direction

            head = (
                snake[0][0] + direction[0],
                snake[0][1] + direction[1]
            )

            eating = head == food

            # Wall collision
            if (
                head[0] < 0 or head[0] >= COLS
                or head[1] < 0 or head[1] >= ROWS
            ):
                state = "GAME_OVER"

            # Self collision
            elif head in (snake if eating else snake[:-1]):
                state = "GAME_OVER"

            else:
                snake.insert(0, head)

                if eating:
                    score += 10

                    if score > best_score:
                        best_score = score
                        save_best()

                    speed = min(20, 9 + score // 50)
                    food = new_food()

                else:
                    snake.pop()

    # ---------------- RENDER ----------------
    if state == "MENU":
        draw_menu()

    elif state == "PLAYING":
        draw_game()

    elif state == "PAUSED":
        draw_pause()

    elif state == "GAME_OVER":
        draw_game_over()

    pygame.display.flip()
