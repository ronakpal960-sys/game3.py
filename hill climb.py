
import pygame
import math
import random
import sys

pygame.init()

# SCREEN SETTINGS
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("HILL CLIMB RACING")

clock = pygame.time.Clock()
FPS = 60

# COLORS
WHITE = (255, 255, 255)
BLACK = (20, 25, 30)
ORANGE = (255, 145, 40)
GREEN = (80, 160, 75)
SKY = (100, 185, 225)

# FONTS
def text(msg, size, color, x, y, center=False):
    f = pygame.font.SysFont("arial", size, bold=True)
    image = f.render(str(msg), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(image, rect)


# GAME VARIABLES
car_x = 250.0
car_y = 400.0
speed = 0.0
velocity_y = 0.0
angle = 0.0

fuel = 100.0
coins = 0
distance = 0
camera = 0.0

game_over = False
paused = False
started = False


# TERRAIN
def ground(x):
    return (
        510
        + 75 * math.sin(x * 0.004)
        + 40 * math.sin(x * 0.009)
        + 25 * math.sin(x * 0.018)
    )


# COINS
coin_list = [
    [700 + i * 400, ground(700 + i * 400) - 120]
    for i in range(50)
]

# FUEL
fuel_list = [
    [1500 + i * 1800, ground(1500 + i * 1800) - 100]
    for i in range(20)
]


# DRAW CAR
def draw_car(x, y, rotation):

    car = pygame.Surface((220, 120), pygame.SRCALPHA)

    pygame.draw.rect(
        car, (35, 45, 50),
        (20, 45, 180, 50),
        border_radius=15
    )

    pygame.draw.rect(
        car, ORANGE,
        (35, 30, 150, 50),
        border_radius=15
    )

    pygame.draw.polygon(
        car, (255, 175, 70),
        [(65, 35), (90, 5), (150, 5), (175, 35)]
    )

    pygame.draw.polygon(
        car, (120, 200, 220),
        [(100, 12), (145, 12), (165, 34), (85, 34)]
    )

    # Wheels
    for wx in [65, 165]:

        pygame.draw.circle(car, BLACK, (wx, 90), 27)
        pygame.draw.circle(car, (170, 180, 185), (wx, 90), 15)
        pygame.draw.circle(car, WHITE, (wx, 90), 6)

    rotated = pygame.transform.rotate(car, rotation)
    rect = rotated.get_rect(center=(int(x), int(y)))

    screen.blit(rotated, rect)


# DRAW TERRAIN
def draw_terrain():

    points = []

    for x in range(-100, WIDTH + 200, 10):

        world_x = x + camera
        points.append((x, int(ground(world_x))))

    polygon = [(0, HEIGHT)] + points + [(WIDTH, HEIGHT)]

    pygame.draw.polygon(screen, GREEN, polygon)

    pygame.draw.lines(
        screen,
        (170, 220, 120),
        False,
        points,
        8
    )


# RESET GAME
def reset():

    global car_x, car_y, speed, velocity_y
    global angle, fuel, coins, distance, camera
    global game_over, paused, started
    global coin_list, fuel_list

    car_x = 250.0
    car_y = ground(car_x) - 100

    speed = 0
    velocity_y = 0
    angle = 0

    fuel = 100
    coins = 0
    distance = 0
    camera = 0

    game_over = False
    paused = False
    started = False

    coin_list = [
        [700 + i * 400, ground(700 + i * 400) - 120]
        for i in range(50)
    ]

    fuel_list = [
        [1500 + i * 1800, ground(1500 + i * 1800) - 100]
        for i in range(20)
    ]


# MAIN GAME LOOP
running = True

while running:

    dt = min(clock.tick(FPS) / 1000, 0.033)

    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            WIDTH = max(640, event.w)
            HEIGHT = max(360, event.h)
            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.RESIZABLE
            )

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_RETURN and not game_over:
                started = True

            if event.key == pygame.K_SPACE and started:
                paused = not paused

            if event.key == pygame.K_r:
                reset()

    keys = pygame.key.get_pressed()

    # SKY
    screen.fill(SKY)

    # SUN
    pygame.draw.circle(
        screen,
        (255, 230, 150),
        (WIDTH - 230, 130),
        65
    )

    # CLOUDS
    for cx, cy in [
        (200, 140),
        (550, 100),
        (850, 210)
    ]:

        pygame.draw.circle(screen, WHITE, (cx, cy), 35)
        pygame.draw.circle(screen, WHITE, (cx + 35, cy), 45)
        pygame.draw.circle(screen, WHITE, (cx + 75, cy), 32)

    # MOUNTAINS
    for x in range(-100, WIDTH + 200, 150):

        h = 250 + 70 * math.sin(
            (x + camera * 0.2) * 0.003
        )

        pygame.draw.polygon(
            screen,
            (105, 145, 160),
            [
                (x, 520),
                (x + 100, int(520 - h)),
                (x + 200, 520)
            ]
        )

    # GAME PHYSICS
    if started and not paused and not game_over:

        # ACCELERATION
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            speed += 650 * dt
            fuel = max(0, fuel - 2 * dt)

        # BRAKE
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            speed -= 500 * dt

        speed *= 0.995
        speed = max(-300, min(speed, 950))

        car_x += speed * dt

        distance = max(distance, int(car_x / 10))

        # GRAVITY
        velocity_y += 1800 * dt
        car_y += velocity_y * dt

        # GROUND COLLISION
        target_y = ground(car_x) - 100

        if car_y >= target_y:
            car_y = target_y
            velocity_y = 0

        # CAR ROTATION
        angle = math.degrees(
            math.atan(
                (ground(car_x + 70) - ground(car_x - 70)) / 140
            )
        )

        # CAMERA
        camera = max(0, car_x - WIDTH * 0.35)

        # COLLECT COINS
        for coin in coin_list:

            if coin[0] > 0 and abs(coin[0] - car_x) < 65:

                if abs(coin[1] - car_y) < 130:

                    coins += 1
                    coin[0] = -1000

        # COLLECT FUEL
        for item in fuel_list:

            if item[0] > 0 and abs(item[0] - car_x) < 65:

                if abs(item[1] - car_y) < 140:

                    fuel = min(100, fuel + 30)
                    item[0] = -1000

        # GAME OVER
        if fuel <= 0 or abs(angle) > 65:
            game_over = True

    # DRAW TERRAIN
    draw_terrain()

    # DRAW COINS
    for coin in coin_list:

        if coin[0] > 0:

            x = int(coin[0] - camera)

            if -50 < x < WIDTH + 50:

                y = int(coin[1])

                pygame.draw.circle(
                    screen, (190, 125, 20), (x, y), 22
                )

                pygame.draw.circle(
                    screen, (255, 205, 40), (x, y), 17
                )

                pygame.draw.circle(
                    screen, (255, 240, 140), (x - 5, y - 6), 5
                )

    # DRAW FUEL
    for item in fuel_list:

        if item[0] > 0:

            x = int(item[0] - camera)

            if -50 < x < WIDTH + 50:

                y = int(item[1])

                pygame.draw.rect(
                    screen, (210, 45, 35),
                    (x - 16, y - 22, 32, 44),
                    border_radius=6
                )

                pygame.draw.rect(
                    screen, WHITE,
                    (x - 5, y - 14, 10, 28)
                )

    # DRAW CAR
    draw_car(car_x - camera, car_y, angle)

    # HUD
    pygame.draw.rect(
        screen, (15, 30, 40),
        (20, 20, 330, 130),
        border_radius=18
    )

    text(f"COINS: {coins}", 27, (255, 210, 50), 40, 35)
    text(f"DISTANCE: {distance} m", 24, WHITE, 40, 75)

    # FUEL BAR
    pygame.draw.rect(
        screen, BLACK,
        (WIDTH - 280, 30, 240, 35),
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        (60, 220, 100) if fuel > 30 else (240, 60, 50),
        (
            WIDTH - 280,
            30,
            max(0, int(240 * fuel / 100)),
            35
        ),
        border_radius=10
    )

    text("FUEL", 23, WHITE, WIDTH - 280, 75)

    # START MENU
    if not started:

        pygame.draw.rect(
            screen,
            (10, 25, 40),
            (250, 230, WIDTH - 500, 230),
            border_radius=25
        )

        text(
            "HILL CLIMB RACING",
            55, WHITE,
            WIDTH // 2, 290, True
        )

        text(
            "PRESS ENTER TO START",
            30, (255, 200, 60),
            WIDTH // 2, 380, True
        )

        text(
            "D / RIGHT = ACCELERATE    A / LEFT = BRAKE",
            22, WHITE,
            WIDTH // 2, 425, True
        )

    # PAUSE MENU
    if paused:

        pygame.draw.rect(
            screen,
            (10, 25, 40),
            (WIDTH // 2 - 200, HEIGHT // 2 - 80, 400, 160),
            border_radius=25
        )

        text(
            "PAUSED",
            65, WHITE,
            WIDTH // 2, HEIGHT // 2, True
        )

    # GAME OVER MENU
    if game_over:

        pygame.draw.rect(
            screen,
            (10, 25, 40),
            (300, 220, WIDTH - 600, 260),
            border_radius=25
        )

        text(
            "GAME OVER",
            60, (255, 90, 70),
            WIDTH // 2, 290, True
        )

        text(
            f"DISTANCE: {distance} m     COINS: {coins}",
            30, WHITE,
            WIDTH // 2, 365, True
        )

        text(
            "PRESS R TO RESTART",
            27, (255, 205, 70),
            WIDTH // 2, 425, True
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
