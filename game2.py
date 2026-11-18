
import pygame
import random
import sys
import math

pygame.init()

# ==========================================
# FULL HD GAME SETTINGS
# ==========================================

W, H = 1920, 1080
FPS = 60

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_W, SCREEN_H = display.get_size()

canvas = pygame.Surface((W, H))
pygame.display.set_caption("FLAPPY BIRD HD")

clock = pygame.time.Clock()

# ==========================================
# COLORS
# ==========================================

WHITE = (255, 255, 255)
BLACK = (20, 30, 45)
YELLOW = (255, 210, 50)
ORANGE = (255, 145, 30)
GREEN = (55, 190, 95)
DARK_GREEN = (25, 125, 65)
BLUE = (75, 175, 240)
NAVY = (30, 65, 105)

# ==========================================
# FONTS
# ==========================================

title_font = pygame.font.SysFont("Arial", 125, bold=True)
large_font = pygame.font.SysFont("Arial", 85, bold=True)
font = pygame.font.SysFont("Arial", 48, bold=True)
small_font = pygame.font.SysFont("Arial", 30)

# ==========================================
# GAME SETTINGS
# ==========================================

GROUND_HEIGHT = 150
GROUND_Y = H - GROUND_HEIGHT

BIRD_X = 430
BIRD_RADIUS = 38

GRAVITY = 1900
JUMP_POWER = -650

PIPE_WIDTH = 145
PIPE_GAP = 330
PIPE_SPEED = 420
PIPE_DISTANCE = 650

# ==========================================
# GAME VARIABLES
# ==========================================

state = "MENU"

bird_y = H // 2
bird_velocity = 0

pipes = []
score = 0
best_score = 0

background_time = 0
ground_offset = 0

particles = []

# ==========================================
# SAVE HIGH SCORE
# ==========================================

try:
    with open("flappy_best.txt", "r") as f:
        best_score = int(f.read())
except:
    best_score = 0


def save_best():
    with open("flappy_best.txt", "w") as f:
        f.write(str(best_score))


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def draw_text(surface, text, font_obj, color, x, y):
    image = font_obj.render(text, True, color)
    rect = image.get_rect(center=(x, y))
    surface.blit(image, rect)


def draw_rounded(surface, color, rect, radius):
    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )


def reset_game():
    global bird_y, bird_velocity, pipes
    global score, state, ground_offset, particles

    bird_y = H // 2
    bird_velocity = 0

    score = 0
    ground_offset = 0
    particles = []

    pipes = []

    first_x = W + 300

    for i in range(4):
        gap_y = random.randint(350, GROUND_Y - 350)

        pipes.append({
            "x": first_x + i * PIPE_DISTANCE,
            "gap_y": gap_y,
            "passed": False
        })


# ==========================================
# BACKGROUND
# ==========================================

def draw_background(surface, dt):

    global background_time

    background_time += dt

    # Sky gradient
    for y in range(0, H, 4):
        t = y / H

        color = (
            int(65 + 90 * t),
            int(165 + 45 * t),
            int(230 - 25 * t)
        )

        pygame.draw.rect(
            surface,
            color,
            (0, y, W, 4)
        )

    # Sun
    pygame.draw.circle(
        surface,
        (255, 235, 155),
        (1550, 190),
        105
    )

    pygame.draw.circle(
        surface,
        (255, 245, 195),
        (1550, 190),
        80
    )

    # Clouds
    for i in range(8):

        x = (i * 330 - background_time * 35) % (W + 400) - 200
        y = 140 + (i % 3) * 125

        pygame.draw.ellipse(
            surface,
            (245, 250, 255),
            (x, y, 180, 65)
        )

        pygame.draw.ellipse(
            surface,
            (255, 255, 255),
            (x + 45, y - 40, 100, 100)
        )

        pygame.draw.ellipse(
            surface,
            (250, 252, 255),
            (x + 100, y - 15, 110, 75)
        )

    # Mountains
    for i in range(7):

        x = i * 350 - (background_time * 20) % 350

        pygame.draw.polygon(
            surface,
            (115, 180, 195),
            [
                (x - 100, GROUND_Y),
                (x + 120, 500),
                (x + 350, GROUND_Y)
            ]
        )

    # Hills
    pygame.draw.rect(
        surface,
        (125, 205, 120),
        (0, GROUND_Y - 75, W, 100)
    )

    for i in range(6):

        x = i * 420 - (background_time * 65) % 420

        pygame.draw.ellipse(
            surface,
            (100, 190, 105),
            (x, GROUND_Y - 110, 550, 150)
        )


# ==========================================
# GROUND
# ==========================================

def draw_ground(surface, dt):

    global ground_offset

    ground_offset += 350 * dt

    if ground_offset >= 100:
        ground_offset = 0

    pygame.draw.rect(
        surface,
        (225, 195, 125),
        (0, GROUND_Y, W, GROUND_HEIGHT)
    )

    pygame.draw.rect(
        surface,
        (75, 190, 85),
        (0, GROUND_Y, W, 28)
    )

    pygame.draw.rect(
        surface,
        (45, 145, 65),
        (0, GROUND_Y + 28, W, 12)
    )

    for x in range(-100, W + 100, 100):

        position = x - ground_offset

        pygame.draw.line(
            surface,
            (195, 160, 105),
            (position, GROUND_Y + 60),
            (position + 40, GROUND_Y + 60),
            4
        )


# ==========================================
# BIRD
# ==========================================

def draw_bird(surface):

    global bird_y

    # Bird rotation
    angle = max(-35, min(35, -bird_velocity / 18))

    bird = pygame.Surface((130, 110), pygame.SRCALPHA)

    # Wing
    pygame.draw.ellipse(
        bird,
        (225, 145, 35),
        (20, 45, 70, 35)
    )

    pygame.draw.ellipse(
        bird,
        YELLOW,
        (15, 20, 85, 65)
    )

    # Belly
    pygame.draw.ellipse(
        bird,
        (255, 235, 160),
        (35, 50, 55, 28)
    )

    # Eye
    pygame.draw.circle(
        bird,
        WHITE,
        (83, 37),
        17
    )

    pygame.draw.circle(
        bird,
        BLACK,
        (89, 38),
        8
    )

    # Beak
    pygame.draw.polygon(
        bird,
        ORANGE,
        [(95, 50), (125, 62), (95, 72)]
    )

    rotated = pygame.transform.rotate(bird, angle)

    rect = rotated.get_rect(
        center=(BIRD_X, int(bird_y))
    )

    surface.blit(rotated, rect)


# ==========================================
# PIPES
# ==========================================

def draw_pipe(surface, pipe):

    x = int(pipe["x"])
    gap = pipe["gap_y"]

    top_height = gap - PIPE_GAP // 2
    bottom_y = gap + PIPE_GAP // 2

    # Top pipe
    top_rect = pygame.Rect(
        x, 0, PIPE_WIDTH, top_height
    )

    # Bottom pipe
    bottom_rect = pygame.Rect(
        x, bottom_y, PIPE_WIDTH, GROUND_Y - bottom_y
    )

    # Pipe shadows
    pygame.draw.rect(
        surface,
        (25, 95, 50),
        top_rect.move(-8, 0)
    )

    pygame.draw.rect(
        surface,
        (25, 95, 50),
        bottom_rect.move(-8, 0)
    )

    # Pipe bodies
    pygame.draw.rect(
        surface,
        GREEN,
        top_rect
    )

    pygame.draw.rect(
        surface,
        GREEN,
        bottom_rect
    )

    # Highlights
    pygame.draw.rect(
        surface,
        (125, 235, 135),
        (x + 18, 0, 15, top_height)
    )

    pygame.draw.rect(
        surface,
        (125, 235, 135),
        (x + 18, bottom_y, 15, GROUND_Y - bottom_y)
    )

    # Pipe caps
    cap_h = 45

    pygame.draw.rect(
        surface,
        DARK_GREEN,
        (x - 12, top_height - cap_h, PIPE_WIDTH + 24, cap_h),
        border_radius=8
    )

    pygame.draw.rect(
        surface,
        GREEN,
        (x - 12, top_height - cap_h, PIPE_WIDTH + 24, cap_h - 8),
        border_radius=8
    )

    pygame.draw.rect(
        surface,
        DARK_GREEN,
        (x - 12, bottom_y, PIPE_WIDTH + 24, cap_h),
        border_radius=8
    )

    pygame.draw.rect(
        surface,
        GREEN,
        (x - 12, bottom_y, PIPE_WIDTH + 24, cap_h - 8),
        border_radius=8
    )


# ==========================================
# PARTICLES
# ==========================================

def create_particles():

    for i in range(12):

        particles.append({
            "x": BIRD_X,
            "y": bird_y,
            "vx": random.uniform(-180, 100),
            "vy": random.uniform(-220, 100),
            "life": 0.6
        })


def update_particles(dt):

    for p in particles[:]:

        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["life"] -= dt

        if p["life"] <= 0:
            particles.remove(p)


def draw_particles(surface):

    for p in particles:

        pygame.draw.circle(
            surface,
            YELLOW,
            (int(p["x"]), int(p["y"])),
            7
        )


# ==========================================
# COLLISION
# ==========================================

def check_collision():

    bird_rect = pygame.Rect(
        BIRD_X - 30,
        int(bird_y) - 28,
        60,
        56
    )

    if bird_y - BIRD_RADIUS < 0:
        return True

    if bird_y + BIRD_RADIUS > GROUND_Y:
        return True

    for pipe in pipes:

        x = int(pipe["x"])
        gap = pipe["gap_y"]

        top_rect = pygame.Rect(
            x, 0, PIPE_WIDTH, gap - PIPE_GAP // 2
        )

        bottom_rect = pygame.Rect(
            x,
            gap + PIPE_GAP // 2,
            PIPE_WIDTH,
            GROUND_Y - (gap + PIPE_GAP // 2)
        )

        if bird_rect.colliderect(top_rect):
            return True

        if bird_rect.colliderect(bottom_rect):
            return True

    return False


# ==========================================
# SCORE DISPLAY
# ==========================================

def draw_score(surface):

    draw_text(
        surface,
        str(score),
        title_font,
        WHITE,
        W // 2,
        125
    )


# ==========================================
# MENU
# ==========================================

def draw_menu(surface):

    draw_background(surface, 0)

    draw_text(
        surface,
        "FLAPPY BIRD",
        title_font,
        WHITE,
        W // 2,
        230
    )

    draw_text(
        surface,
        "HD ARCADE EDITION",
        font,
        YELLOW,
        W // 2,
        325
    )

    # Menu card
    card = pygame.Rect(610, 410, 700, 360)

    draw_rounded(
        surface,
        (255, 255, 255),
        card,
        35
    )

    draw_text(
        surface,
        "READY TO FLY?",
        large_font,
        NAVY,
        W // 2,
        500
    )

    draw_text(
        surface,
        "Press SPACE or CLICK to start",
        font,
        (75, 100, 125),
        W // 2,
        600
    )

    draw_text(
        surface,
        f"BEST SCORE: {best_score}",
        font,
        DARK_GREEN,
        W // 2,
        690
    )

    draw_text(
        surface,
        "ESC = QUIT",
        small_font,
        WHITE,
        W // 2,
        930
    )

    # Bird preview
    global bird_y
    bird_y = 850 + math.sin(pygame.time.get_ticks() / 350) * 18

    draw_bird(surface)
    draw_ground(surface, 0)


# ==========================================
# GAME OVER
# ==========================================

def draw_game_over(surface):

    draw_background(surface, 0)

    for pipe in pipes:
        draw_pipe(surface, pipe)

    draw_ground(surface, 0)
    draw_bird(surface)

    # Overlay
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((10, 20, 40, 160))
    surface.blit(overlay, (0, 0))

    card = pygame.Rect(610, 280, 700, 550)

    draw_rounded(
        surface,
        (250, 253, 255),
        card,
        35
    )

    draw_text(
        surface,
        "GAME OVER",
        large_font,
        (225, 75, 75),
        W // 2,
        390
    )

    draw_text(
        surface,
        "YOUR SCORE",
        font,
        GREY_COLOR,
        W // 2,
        500
    )

    draw_text(
        surface,
        str(score),
        title_font,
        NAVY,
        W // 2,
        590
    )

    draw_text(
        surface,
        f"BEST SCORE: {best_score}",
        font,
        DARK_GREEN,
        W // 2,
        680
    )

    draw_text(
        surface,
        "PRESS SPACE OR CLICK TO PLAY AGAIN",
        small_font,
        NAVY,
        W // 2,
        760
    )


GREY_COLOR = (115, 130, 150)


# ==========================================
# PAUSE SCREEN
# ==========================================

def draw_pause(surface):

    draw_background(surface, 0)

    for pipe in pipes:
        draw_pipe(surface, pipe)

    draw_ground(surface, 0)
    draw_bird(surface)

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((10, 20, 40, 175))
    surface.blit(overlay, (0, 0))

    draw_text(
        surface,
        "PAUSED",
        title_font,
        WHITE,
        W // 2,
        450
    )

    draw_text(
        surface,
        "Press P or SPACE to continue",
        font,
        YELLOW,
        W // 2,
        570
    )


# ==========================================
# RESET GAME
# ==========================================

reset_game()

# ==========================================
# MAIN GAME LOOP
# ==========================================

running = True

while running:

    dt = min(clock.tick(FPS) / 1000, 0.04)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if state == "MENU":

                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    reset_game()
                    state = "PLAYING"

            elif state == "PLAYING":

                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    bird_velocity = JUMP_POWER
                    create_particles()

                elif event.key == pygame.K_p:
                    state = "PAUSED"

            elif state == "PAUSED":

                if event.key in (pygame.K_p, pygame.K_SPACE):
                    state = "PLAYING"

            elif state == "GAME_OVER":

                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_r):
                    reset_game()
                    state = "PLAYING"

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if state == "MENU":
                    reset_game()
                    state = "PLAYING"

                elif state == "PLAYING":
                    bird_velocity = JUMP_POWER
                    create_particles()

                elif state == "GAME_OVER":
                    reset_game()
                    state = "PLAYING"

    # ======================================
    # UPDATE GAME
    # ======================================

    if state == "PLAYING":

        bird_velocity += GRAVITY * dt
        bird_y += bird_velocity * dt

        # Move pipes
        for pipe in pipes:

            pipe["x"] -= PIPE_SPEED * dt

            # Score
            if not pipe["passed"] and pipe["x"] + PIPE_WIDTH < BIRD_X:

                pipe["passed"] = True
                score += 1

                if score > best_score:
                    best_score = score
                    save_best()

        # Remove old pipes
        pipes = [
            p for p in pipes
            if p["x"] > -PIPE_WIDTH - 50
        ]

        # Add new pipes
        if pipes and pipes[-1]["x"] < W - PIPE_DISTANCE:

            gap_y = random.randint(
                350,
                GROUND_Y - 350
            )

            pipes.append({
                "x": W + 50,
                "gap_y": gap_y,
                "passed": False
            })

        # Collision
        if check_collision():
            state = "GAME_OVER"

        update_particles(dt)

    # ======================================
    # DRAW SCREEN
    # ======================================

    if state == "MENU":

        draw_menu(canvas)

    elif state == "PLAYING":

        draw_background(canvas, dt)

        for pipe in pipes:
            draw_pipe(canvas, pipe)

        draw_ground(canvas, dt)
        draw_particles(canvas)
        draw_bird(canvas)
        draw_score(canvas)

        draw_text(
            canvas,
            f"BEST: {best_score}",
            small_font,
            WHITE,
            1750,
            65
        )

        draw_text(
            canvas,
            "P = PAUSE",
            small_font,
            WHITE,
            1750,
            115
        )

    elif state == "PAUSED":

        draw_pause(canvas)

    elif state == "GAME_OVER":

        draw_game_over(canvas)

    # ======================================
    # FULL SCREEN SCALING
    # ======================================

    scaled = pygame.transform.smoothscale(
        canvas,
        (SCREEN_W, SCREEN_H)
    )

    display.blit(scaled, (0, 0))

    pygame.display.flip()


pygame.quit()
sys.exit()
