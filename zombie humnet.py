
import pygame
import random
import math
import sys

pygame.init()

# ================= SETTINGS =================
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("ZOMBIE HUNTER - APOCALYPSE")

clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (15, 20, 25)
GREEN = (70, 210, 100)
RED = (240, 65, 65)
GOLD = (255, 205, 55)
ORANGE = (255, 145, 45)

# ================= FONTS =================
def draw_text(msg, size, color, x, y, center=False):
    f = pygame.font.SysFont("arial", size, bold=True)
    img = f.render(str(msg), True, color)
    rect = img.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(img, rect)


# ================= GAME VARIABLES =================
state = "menu"

player_level = 1
xp = 0
xp_needed = 100

coins = 0
score = 0
health = 100

wave = 1
zombies_killed = 0

weapon_level = 1
bombs = 0

car_x = 250
car_y = 490

road_offset = 0

zombies = []
bullets = []
particles = []

wave_spawned = 0
wave_total = 6
spawn_timer = 0

boss = None
boss_spawned = False

shoot_cooldown = 0
bomb_flash = 0

# ================= WEAPONS =================
WEAPONS = {
    1: ("ENERGY BLASTER", 1, 18),
    2: ("RAPID BLASTER", 2, 12),
    3: ("PLASMA CANNON", 3, 9),
    4: ("MEGA PLASMA", 4, 7)
}

def weapon_name():
    return WEAPONS[weapon_level][0]


# ================= CAR =================
def draw_car(x, y):

    car = pygame.Surface((240, 140), pygame.SRCALPHA)

    pygame.draw.rect(
        car, (35, 45, 50),
        (15, 48, 210, 65),
        border_radius=20
    )

    pygame.draw.rect(
        car, (210, 90, 35),
        (35, 25, 160, 70),
        border_radius=18
    )

    pygame.draw.polygon(
        car, (245, 140, 55),
        [(70, 30), (95, 3), (165, 3), (190, 30)]
    )

    pygame.draw.polygon(
        car, (100, 190, 215),
        [(105, 10), (158, 10), (178, 30), (85, 30)]
    )

    pygame.draw.rect(
        car, (70, 75, 80),
        (40, 85, 155, 13),
        border_radius=5
    )

    # Wheels
    for wx in [60, 185]:
        pygame.draw.circle(car, BLACK, (wx, 110), 26)
        pygame.draw.circle(car, (150, 160, 165), (wx, 110), 14)
        pygame.draw.circle(car, WHITE, (wx, 110), 5)

    # Headlight
    pygame.draw.circle(car, (255, 245, 150), (220, 72), 10)

    screen.blit(car, (x, y))


# ================= ZOMBIES =================
class Zombie:

    def __init__(self, boss=False):

        self.boss = boss

        self.x = WIDTH + random.randint(40, 300)
        self.y = random.randint(440, 520)

        if boss:
            self.size = 90
            self.hp = 15 + wave * 4
            self.speed = random.uniform(45, 65)
        else:
            self.size = random.randint(45, 65)
            self.hp = 2 + wave // 3
            self.speed = random.uniform(65, 110) + wave * 3

        self.max_hp = self.hp
        self.phase = random.random() * 6

    def update(self, dt):

        self.x -= self.speed * dt
        self.phase += dt * 5

        self.y += math.sin(self.phase) * 0.3

    def draw(self):

        size = self.size

        color = (105, 155, 75) if not self.boss else (145, 75, 85)

        # Body
        pygame.draw.rect(
            screen, color,
            (int(self.x), int(self.y), size, size),
            border_radius=12
        )

        # Head
        pygame.draw.circle(
            screen, color,
            (int(self.x + size // 2), int(self.y - 12)),
            size // 2
        )

        # Eyes
        pygame.draw.circle(
            screen, RED,
            (int(self.x + size * .32), int(self.y - 15)),
            5
        )

        pygame.draw.circle(
            screen, RED,
            (int(self.x + size * .68), int(self.y - 15)),
            5
        )

        # Mouth
        pygame.draw.line(
            screen, BLACK,
            (int(self.x + size * .3), int(self.y + 3)),
            (int(self.x + size * .7), int(self.y + 3)),
            4
        )

        # Arms
        pygame.draw.line(
            screen, color,
            (int(self.x), int(self.y + 20)),
            (int(self.x - 15), int(self.y + 45)),
            10
        )

        pygame.draw.line(
            screen, color,
            (int(self.x + size), int(self.y + 20)),
            (int(self.x + size + 15), int(self.y + 45)),
            10
        )

        # Health bar
        bar_width = size

        pygame.draw.rect(
            screen, BLACK,
            (self.x, self.y - 42, bar_width, 9)
        )

        pygame.draw.rect(
            screen, RED,
            (self.x, self.y - 42,
             bar_width * max(0, self.hp) / self.max_hp, 9)
        )


# ================= PROJECTILES =================
class Bullet:

    def __init__(self, x, y, damage):

        self.x = x
        self.y = y
        self.speed = 850
        self.damage = damage

    def update(self, dt):
        self.x += self.speed * dt

    def draw(self):

        pygame.draw.circle(
            screen, (80, 230, 255),
            (int(self.x), int(self.y)), 10
        )

        pygame.draw.circle(
            screen, WHITE,
            (int(self.x), int(self.y)), 4
        )


# ================= PARTICLES =================
def create_particles(x, y):

    for _ in range(12):

        particles.append([
            x, y,
            random.uniform(-150, 150),
            random.uniform(-180, 100),
            random.randint(3, 7),
            0.5
        ])


def update_particles(dt):

    for p in particles[:]:

        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[5] -= dt

        pygame.draw.circle(
            screen, ORANGE,
            (int(p[0]), int(p[1])),
            max(1, int(p[4] * p[5] * 2))
        )

        if p[5] <= 0:
            particles.remove(p)


# ================= XP SYSTEM =================
def add_xp(amount):

    global xp, player_level, xp_needed, weapon_level

    xp += amount

    while xp >= xp_needed:

        xp -= xp_needed
        player_level += 1
        xp_needed = int(xp_needed * 1.35)

        # Upgrade weapon at certain levels
        if player_level == 3:
            weapon_level = 2

        elif player_level == 6:
            weapon_level = 3

        elif player_level == 10:
            weapon_level = 4


# ================= KILL ZOMBIE =================
def kill_zombie(z):

    global coins, score, zombies_killed, boss

    coins += 15 if not z.boss else 100
    score += 100 if not z.boss else 1000

    zombies_killed += 1

    add_xp(25 if not z.boss else 120)

    create_particles(z.x, z.y)

    if z.boss:
        boss = None
        return

    if random.random() < 0.08:
        pass


# ================= RESET =================
def reset_game():

    global state, player_level, xp, xp_needed
    global coins, score, health, wave
    global zombies_killed, weapon_level, bombs
    global zombies, bullets, particles
    global wave_spawned, wave_total, spawn_timer
    global boss, boss_spawned, car_x, road_offset

    state = "playing"

    player_level = 1
    xp = 0
    xp_needed = 100

    coins = 0
    score = 0
    health = 100

    wave = 1
    zombies_killed = 0

    weapon_level = 1
    bombs = 0

    zombies = []
    bullets = []
    particles = []

    wave_spawned = 0
    wave_total = 6
    spawn_timer = 0

    boss = None
    boss_spawned = False

    car_x = 250
    road_offset = 0


# ================= BOMB =================
def use_bomb():

    global bombs, bomb_flash, boss

    if bombs <= 0:
        return

    bombs -= 1
    bomb_flash = 0.5

    for z in zombies[:]:

        create_particles(z.x, z.y)

        if z.boss:
            z.hp -= 8

            if z.hp <= 0:
                kill_zombie(z)
        else:
            kill_zombie(z)
            zombies.remove(z)

    # Bomb is a screen-clearing arcade power-up.
    # It does not use realistic explosive mechanics.


# ================= HUD =================
def draw_hud():

    # Top panel
    pygame.draw.rect(
        screen, (12, 24, 35),
        (15, 15, 460, 155),
        border_radius=18
    )

    draw_text(f"SCORE: {score}", 25, WHITE, 35, 28)
    draw_text(f"COINS: {coins}", 24, GOLD, 35, 65)
    draw_text(f"WAVE: {wave}", 24, ORANGE, 260, 28)
    draw_text(f"LEVEL: {player_level}", 24, GREEN, 260, 65)

    draw_text(
        f"WEAPON: {weapon_name()}",
        20, (100, 220, 255), 35, 112
    )

    # XP BAR
    pygame.draw.rect(
        screen, BLACK,
        (500, 30, 330, 22),
        border_radius=10
    )

    pygame.draw.rect(
        screen, (80, 220, 130),
        (500, 30, int(330 * xp / xp_needed), 22),
        border_radius=10
    )

    draw_text("EXPERIENCE", 17, WHITE, 500, 58)

    # Health
    pygame.draw.rect(
        screen, BLACK,
        (WIDTH - 300, 30, 260, 28),
        border_radius=10
    )

    pygame.draw.rect(
        screen, RED,
        (WIDTH - 300, 30, int(260 * health / 100), 28),
        border_radius=10
    )

    draw_text("HEALTH", 19, WHITE, WIDTH - 300, 65)

    # Bomb
    pygame.draw.rect(
        screen, (65, 45, 35),
        (WIDTH - 205, 110, 165, 65),
        border_radius=12
    )

    draw_text(
        f"BOMB: {bombs}",
        23, GOLD,
        WIDTH - 125, 142, True
    )

    draw_text(
        "PRESS B",
        15, WHITE,
        WIDTH - 125, 165, True
    )


# ================= MAIN LOOP =================
running = True

while running:

    dt = min(clock.tick(FPS) / 1000, 0.033)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:

            WIDTH = max(800, event.w)
            HEIGHT = max(500, event.h)

            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.RESIZABLE
            )

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_RETURN and state == "menu":
                reset_game()

            if event.key == pygame.K_r and state == "gameover":
                reset_game()

            if event.key == pygame.K_SPACE and state == "playing":
                pass

            if event.key == pygame.K_b and state == "playing":
                use_bomb()

    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()

    # ================= BACKGROUND =================
    screen.fill((85, 150, 185))

    # Sky
    pygame.draw.circle(
        screen, (255, 220, 130),
        (WIDTH - 140, 130), 60
    )

    # Distant buildings
    for i in range(12):

        bx = i * 140 - (int(road_offset * 0.2) % 140)

        pygame.draw.rect(
            screen, (65, 83, 92),
            (bx, 300, 95, 260)
        )

        for wy in range(330, 520, 45):

            pygame.draw.rect(
                screen, (210, 190, 110),
                (bx + 15, wy, 18, 22)
            )

            pygame.draw.rect(
                screen, (210, 190, 110),
                (bx + 55, wy, 18, 22)
            )

    # Ground
    pygame.draw.rect(
        screen, (75, 105, 62),
        (0, 540, WIDTH, HEIGHT - 540)
    )

    # Road
    pygame.draw.rect(
        screen, (65, 65, 70),
        (0, 550, WIDTH, 130)
    )

    # Road lines
    road_offset += 250 * dt if state == "playing" else 0

    for i in range(-1, WIDTH // 100 + 2):

        rx = i * 100 - int(road_offset % 100)

        pygame.draw.rect(
            screen, (235, 210, 145),
            (rx, 610, 55, 8)
        )

    # ================= GAME =================
    if state == "playing":

        # Car movement
        car_x = 250

        # Wave spawning
        if wave_spawned < wave_total:

            spawn_timer -= dt

            if spawn_timer <= 0:

                z = Zombie()
                zombies.append(z)

                wave_spawned += 1
                spawn_timer = random.uniform(1.0, 2.2)

        # Boss every third wave
        if wave % 3 == 0 and not boss_spawned:

            boss = Zombie(boss=True)
            zombies.append(boss)
            boss_spawned = True

        # Shooting
        shoot_cooldown -= dt

        if (keys[pygame.K_SPACE] or mouse[0]) and shoot_cooldown <= 0:

            damage = weapon_level * 2

            bullets.append(
                Bullet(car_x + 200, car_y + 70, damage)
            )

            shoot_cooldown = WEAPONS[weapon_level][2] / 100

        # Update bullets
        for bullet in bullets[:]:

            bullet.update(dt)
            bullet.draw()

            if bullet.x > WIDTH:
                bullets.remove(bullet)
                continue

            for z in zombies[:]:

                if (
                    abs(bullet.x - z.x - z.size / 2) < z.size / 2 + 12
                    and abs(bullet.y - z.y) < z.size
                ):

                    z.hp -= bullet.damage
                    create_particles(bullet.x, bullet.y)

                    if bullet in bullets:
                        bullets.remove(bullet)

                    if z.hp <= 0:

                        kill_zombie(z)

                        if z in zombies:
                            zombies.remove(z)

                    break

        # Update zombies
        for z in zombies[:]:

            z.update(dt)
            z.draw()

            # Zombie reaches car
            if z.x < car_x + 150:

                health -= 18 * dt if not z.boss else 30 * dt
                z.x = car_x + 150

                if health <= 0:
                    health = 0
                    state = "gameover"

        # Wave complete
        if (
            wave_spawned >= wave_total
            and len(zombies) == 0
            and state == "playing"
        ):

            wave += 1
            wave_spawned = 0
            wave_total += 3
            spawn_timer = 2
            boss_spawned = False

            # Bonus after every wave
            coins += 50
            bombs += 1

        # Car
        draw_car(car_x, car_y)

        # Particles
        update_particles(dt)

        # Bomb flash
        if bomb_flash > 0:

            bomb_flash -= dt

            flash = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            flash.fill((255, 240, 180, 90))
            screen.blit(flash, (0, 0))

        draw_hud()

        draw_text(
            "SPACE / LEFT CLICK = SHOOT",
            19, WHITE, 20, HEIGHT - 38
        )

        draw_text(
            "B = BOMB",
            19, GOLD, 330, HEIGHT - 38
        )

    # ================= MENU =================
    elif state == "menu":

        draw_car(220, 490)

        pygame.draw.rect(
            screen, (10, 22, 35),
            (WIDTH // 2 - 330, 180, 660, 340),
            border_radius=25
        )

        draw_text(
            "ZOMBIE HUNTER",
            65, (90, 230, 130),
            WIDTH // 2, 260, True
        )

        draw_text(
            "APOCALYPSE SURVIVAL",
            28, WHITE,
            WIDTH // 2, 325, True
        )

        draw_text(
            "PRESS ENTER TO START",
            30, GOLD,
            WIDTH // 2, 420, True
        )

        draw_text(
            "SPACE / CLICK TO SHOOT",
            20, WHITE,
            WIDTH // 2, 470, True
        )

    # ================= GAME OVER =================
    elif state == "gameover":

        pygame.draw.rect(
            screen, (10, 20, 32),
            (WIDTH // 2 - 300, 180, 600, 350),
            border_radius=25
        )

        draw_text(
            "GAME OVER",
            65, RED,
            WIDTH // 2, 260, True
        )

        draw_text(
            f"SCORE: {score}",
            32, WHITE,
            WIDTH // 2, 335, True
        )

        draw_text(
            f"WAVE: {wave}     LEVEL: {player_level}",
            26, GOLD,
            WIDTH // 2, 385, True
        )

        draw_text(
            "PRESS R TO RESTART",
            30, GREEN,
            WIDTH // 2, 465, True
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
