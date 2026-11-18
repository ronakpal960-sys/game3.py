
import pygame
import random
import math
import sys

pygame.init()
pygame.mixer.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1920, 1080
FPS = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FRUIT NINJA - PREMIUM ARCADE")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (10, 12, 25)
GOLD = (255, 205, 70)
RED = (255, 70, 80)
CYAN = (50, 220, 255)

font_big = pygame.font.SysFont("arial", 100, bold=True)
font_medium = pygame.font.SysFont("arial", 48, bold=True)
font_small = pygame.font.SysFont("arial", 30, bold=True)

# ---------------- GAME STATE ----------------
MENU = 0
PLAYING = 1
GAMEOVER = 2

state = MENU
score = 0
lives = 3
best_score = 0

fruits = []
particles = []
floating_texts = []
blade = []

spawn_timer = 0
combo = 0
shake = 0

# ---------------- BACKGROUND ----------------
background = pygame.Surface((WIDTH, HEIGHT))

for y in range(HEIGHT):
    ratio = y / HEIGHT
    color = (
        int(8 + ratio * 12),
        int(12 + ratio * 15),
        int(32 + ratio * 25)
    )
    pygame.draw.line(background, color, (0, y), (WIDTH, y))

# Background decoration
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    pygame.draw.circle(
        background,
        (25, 38, 65),
        (x, y),
        random.randint(1, 3)
    )

# ---------------- FRUIT COLORS ----------------
fruit_types = [
    ("WATERMELON", (255, 65, 90)),
    ("ORANGE", (255, 155, 35)),
    ("APPLE", (235, 45, 65)),
    ("KIWI", (135, 210, 75)),
    ("BLUEBERRY", (90, 120, 255)),
    ("LEMON", (255, 225, 55))
]


class Fruit:
    def __init__(self, bomb=False):
        self.x = random.randint(180, WIDTH - 180)
        self.y = HEIGHT + 100

        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-25, -19)

        self.radius = random.randint(42, 65)
        self.bomb = bomb

        self.rotation = random.randint(0, 360)
        self.rot_speed = random.uniform(-4, 4)

        self.sliced = False

        self.color = (
            (25, 25, 35)
            if bomb else random.choice(fruit_types)[1]
        )

        self.trail = []

    def update(self):
        self.vy += 0.34
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed

        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

    def draw(self):
        if self.sliced:
            return

        x, y = int(self.x), int(self.y)
        r = self.radius

        # Shadow
        pygame.draw.circle(
            screen, (0, 0, 0), (x + 8, y + 10), r
        )

        if self.bomb:
            pygame.draw.circle(screen, (30, 30, 40), (x, y), r)
            pygame.draw.circle(screen, (100, 100, 115), (x, y), r, 4)

            pygame.draw.circle(
                screen, (255, 90, 35),
                (x + 18, y - 35), 10
            )

            pygame.draw.line(
                screen, (255, 170, 45),
                (x + 15, y - 45),
                (x + 28, y - 58), 5
            )

            pygame.draw.circle(
                screen, (255, 255, 150),
                (x - 15, y - 15), 8
            )
        else:
            pygame.draw.circle(screen, self.color, (x, y), r)

            pygame.draw.circle(
                screen, (255, 255, 255),
                (x - r // 3, y - r // 3),
                r // 5
            )

            pygame.draw.circle(
                screen,
                tuple(max(0, c - 50) for c in self.color),
                (x, y), r, 4
            )

            # Fruit leaf
            pygame.draw.ellipse(
                screen, (80, 220, 90),
                (x + 5, y - r - 12, 25, 13)
            )


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

        angle = random.uniform(0, math.tau)
        speed = random.uniform(3, 12)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = 35
        self.size = random.randint(3, 9)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(self.y)),
                max(1, int(self.size * self.life / 35))
            )


# ---------------- UI FUNCTIONS ----------------
def draw_text(text, font, color, x, y, center=True):
    image = font.render(text, True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(image, rect)


def button(text, x, y, w, h, mouse):
    rect = pygame.Rect(x, y, w, h)

    color = (35, 105, 160) if rect.collidepoint(mouse) else (24, 65, 110)

    pygame.draw.rect(screen, color, rect, border_radius=22)
    pygame.draw.rect(screen, CYAN, rect, 3, border_radius=22)

    draw_text(text, font_medium, WHITE, x + w // 2, y + h // 2)

    return rect


def reset_game():
    global score, lives, fruits, particles
    global floating_texts, spawn_timer, combo

    score = 0
    lives = 3
    combo = 0

    fruits.clear()
    particles.clear()
    floating_texts.clear()

    spawn_timer = 0


def add_explosion(x, y, color, amount=25):
    for _ in range(amount):
        particles.append(Particle(x, y, color))


def slice_fruit(fruit):
    global score, shake, combo

    if fruit.bomb:
        return

    fruit.sliced = True
    score += 10
    combo += 1

    add_explosion(fruit.x, fruit.y, fruit.color, 35)

    floating_texts.append(
        [fruit.x, fruit.y, "+10", 40]
    )


# ---------------- MAIN LOOP ----------------
running = True

while running:
    dt = clock.tick(FPS)
    mouse = pygame.mouse.get_pos()

    # Background
    screen.blit(background, (0, 0))

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_RETURN and state == MENU:
                reset_game()
                state = PLAYING

            if event.key == pygame.K_r and state == GAMEOVER:
                reset_game()
                state = PLAYING

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == MENU:
                if start_button.collidepoint(mouse):
                    reset_game()
                    state = PLAYING

            elif state == GAMEOVER:
                if restart_button.collidepoint(mouse):
                    reset_game()
                    state = PLAYING

        if event.type == pygame.MOUSEMOTION and state == PLAYING:
            if event.buttons[0]:
                blade.append(mouse)

                if len(blade) > 12:
                    blade.pop(0)

                for fruit in fruits:
                    if fruit.sliced:
                        continue

                    distance = math.hypot(
                        fruit.x - mouse[0],
                        fruit.y - mouse[1]
                    )

                    if distance < fruit.radius + 12:
                        if fruit.bomb:
                            shake = 25
                            add_explosion(
                                fruit.x, fruit.y, RED, 65
                            )
                            state = GAMEOVER
                            break
                        else:
                            slice_fruit(fruit)

        if event.type == pygame.MOUSEBUTTONUP:
            blade.clear()

    # ---------------- MENU ----------------
    if state == MENU:

        draw_text(
            "FRUIT NINJA",
            font_big, GOLD,
            WIDTH // 2, 300
        )

        draw_text(
            "PREMIUM ARCADE EDITION",
            font_medium, CYAN,
            WIDTH // 2, 390
        )

        draw_text(
            "SLICE FRUITS  |  AVOID BOMBS",
            font_small, WHITE,
            WIDTH // 2, 500
        )

        start_button = button(
            "START GAME",
            WIDTH // 2 - 190, 600,
            380, 95, mouse
        )

        draw_text(
            "Press ENTER to Play",
            font_small, WHITE,
            WIDTH // 2, 780
        )

    # ---------------- PLAYING ----------------
    elif state == PLAYING:

        # HUD
        pygame.draw.rect(
            screen, (20, 30, 60),
            (30, 25, WIDTH - 60, 100),
            border_radius=25
        )

        draw_text(
            f"SCORE: {score}",
            font_medium, GOLD,
            100, 50, False
        )

        draw_text(
            f"LIVES: {lives}",
            font_medium, RED,
            WIDTH - 320, 50, False
        )

        draw_text(
            f"BEST: {best_score}",
            font_medium, CYAN,
            WIDTH // 2 - 100, 50, False
        )

        # Spawn fruits
        spawn_timer += dt

        if spawn_timer > 850:
            spawn_timer = 0

            for _ in range(random.randint(2, 4)):
                fruits.append(Fruit())

            # Random bomb
            if random.random() < 0.28:
                fruits.append(Fruit(bomb=True))

        # Update and draw fruits
        for fruit in fruits[:]:
            fruit.update()
            fruit.draw()

            if fruit.y > HEIGHT + 150:
                if not fruit.sliced and not fruit.bomb:
                    lives -= 1

                fruits.remove(fruit)

        # Particles
        for particle in particles[:]:
            particle.update()
            particle.draw()

            if particle.life <= 0:
                particles.remove(particle)

        # Floating score
        for item in floating_texts[:]:
            item[1] -= 2
            item[3] -= 1

            draw_text(
                item[2], font_small,
                GOLD, int(item[0]), int(item[1])
            )

            if item[3] <= 0:
                floating_texts.remove(item)

        # Blade effect
        if len(blade) > 1:
            for i in range(1, len(blade)):
                alpha_width = max(2, 14 - i)

                pygame.draw.line(
                    screen, CYAN,
                    blade[i - 1], blade[i],
                    alpha_width
                )

        if lives <= 0:
            state = GAMEOVER

    # ---------------- GAME OVER ----------------
    elif state == GAMEOVER:

        best_score = max(best_score, score)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))

        draw_text(
            "GAME OVER",
            font_big, RED,
            WIDTH // 2, 300
        )

        draw_text(
            f"YOUR SCORE: {score}",
            font_medium, GOLD,
            WIDTH // 2, 450
        )

        draw_text(
            f"BEST SCORE: {best_score}",
            font_medium, CYAN,
            WIDTH // 2, 530
        )

        restart_button = button(
            "PLAY AGAIN",
            WIDTH // 2 - 190, 650,
            380, 95, mouse
        )

        draw_text(
            "Press R to Restart",
            font_small, WHITE,
            WIDTH // 2, 820
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
