
import pygame
import random
import math
import sys

pygame.init()

# ==========================================
# PUZZLE WORLD - ULTIMATE EDITION
# ==========================================

WIDTH, HEIGHT = 1150, 800
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PUZZLE WORLD | Ultimate Edition")
clock = pygame.time.Clock()

# COLORS
BG = (12, 16, 30)
PANEL = (24, 32, 52)
PANEL2 = (34, 44, 68)
WHITE = (245, 248, 255)
MUTED = (145, 160, 185)
CYAN = (50, 220, 235)
PURPLE = (155, 105, 255)
GREEN = (65, 225, 155)
ORANGE = (255, 165, 70)
RED = (255, 90, 110)

FONT = pygame.font.SysFont("segoeui", 21)
SMALL = pygame.font.SysFont("segoeui", 16)
MEDIUM = pygame.font.SysFont("segoeui", 27, bold=True)
BIG = pygame.font.SysFont("segoeui", 43, bold=True)

# GAME SETTINGS
BOARD_X = 65
BOARD_Y = 210
BOARD_SIZE = 440

PREVIEW_X = 620
PREVIEW_Y = 230
PREVIEW_SIZE = 300

# ==========================================
# PUZZLE COLLECTION
# ==========================================

PUZZLES = [
    ("ANIMAL", "Lion King", (255, 170, 45)),
    ("ANIMAL", "Cute Panda", (235, 235, 245)),
    ("ANIMAL", "Wild Tiger", (245, 115, 35)),
    ("ANIMAL", "Elephant", (140, 155, 180)),
    ("ANIMAL", "Wolf", (165, 180, 200)),
    ("ANIMAL", "Funny Monkey", (155, 100, 65)),
    ("VEGETABLE", "Fresh Carrot", (255, 120, 35)),
    ("VEGETABLE", "Red Tomato", (235, 65, 70)),
    ("VEGETABLE", "Broccoli", (65, 170, 90)),
    ("VEGETABLE", "Pumpkin", (245, 135, 35)),
    ("VEGETABLE", "Purple Eggplant", (130, 80, 190)),
    ("FRUIT", "Watermelon", (70, 190, 105)),
    ("FRUIT", "Golden Banana", (250, 210, 55)),
    ("CREATURE", "Fire Dragon", (210, 65, 65)),
    ("CREATURE", "Dark Monster", (115, 75, 190)),
    ("CREATURE", "Dinosaur", (75, 185, 105)),
    ("CREATURE", "Alien", (65, 205, 180)),
    ("CREATURE", "Ice Beast", (90, 175, 235)),
    ("NORMAL", "Space Rocket", (90, 130, 245)),
    ("NORMAL", "Magic Planet", (115, 100, 220)),
    ("NORMAL", "Treasure Chest", (220, 155, 55)),
    ("NORMAL", "Fantasy Castle", (175, 130, 235)),
]

# ==========================================
# DRAW HELPERS
# ==========================================

def text(txt, font, color, x, y, center=False):
    img = font.render(str(txt), True, color)
    rect = img.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(img, rect)


def panel(rect, color=PANEL, radius=16):
    pygame.draw.rect(screen, color, rect, border_radius=radius)


def button(label, rect, color):
    mouse = pygame.mouse.get_pos()
    r = pygame.Rect(rect)

    draw_color = color

    if r.collidepoint(mouse):
        draw_color = tuple(min(255, v + 25) for v in color)

    panel(r, draw_color, 12)

    text(label, FONT, WHITE, r.centerx, r.centery, True)

    return r


def draw_background():
    screen.fill(BG)

    pygame.draw.circle(screen, (24, 35, 72), (0, 0), 260)
    pygame.draw.circle(screen, (35, 25, 70), (WIDTH, HEIGHT), 270)

    for i in range(35):
        x = (i * 197) % WIDTH
        y = (i * 113) % HEIGHT
        pygame.draw.circle(screen, (42, 57, 85), (x, y), 2)


# ==========================================
# PROCEDURAL PUZZLE ART
# ==========================================

def make_art(category, name, base_color):
    surface = pygame.Surface((600, 600))
    surface.fill((30, 45, 75))

    # Background gradient
    for y in range(600):
        t = y / 600
        color = (
            int(25 + 35 * t),
            int(45 + 25 * t),
            int(85 + 30 * t)
        )
        pygame.draw.line(surface, color, (0, y), (600, y))

    # Decorative stars
    random.seed(sum(ord(c) for c in name))

    for i in range(65):
        x = random.randint(0, 599)
        y = random.randint(0, 599)
        radius = random.randint(1, 3)

        pygame.draw.circle(
            surface,
            (175, 195, 230),
            (x, y),
            radius
        )

    # Ground
    pygame.draw.ellipse(
        surface,
        (38, 125, 100),
        (-80, 440, 760, 260)
    )

    # Sun
    pygame.draw.circle(surface, (255, 205, 100), (475, 115), 62)

    color = base_color

    if category in ("ANIMAL", "CREATURE"):

        # Character body
        pygame.draw.ellipse(
            surface, color,
            (185, 250, 235, 230)
        )

        # Head
        pygame.draw.circle(
            surface, color, (300, 235), 135
        )

        # Ears
        pygame.draw.circle(
            surface, color, (205, 140), 48
        )

        pygame.draw.circle(
            surface, color, (395, 140), 48
        )

        pygame.draw.circle(
            surface, (255, 180, 190), (205, 140), 23
        )

        pygame.draw.circle(
            surface, (255, 180, 190), (395, 140), 23
        )

        # Creature horns
        if category == "CREATURE":
            pygame.draw.polygon(
                surface, (235, 230, 220),
                [(220, 150), (185, 55), (265, 125)]
            )

            pygame.draw.polygon(
                surface, (235, 230, 220),
                [(380, 150), (415, 55), (335, 125)]
            )

        # Eyes
        pygame.draw.circle(surface, WHITE, (255, 225), 24)
        pygame.draw.circle(surface, WHITE, (345, 225), 24)

        pygame.draw.circle(surface, (25, 30, 40), (260, 225), 11)
        pygame.draw.circle(surface, (25, 30, 40), (350, 225), 11)

        # Nose
        pygame.draw.ellipse(
            surface, (35, 30, 35),
            (280, 275, 42, 30)
        )

        # Smile
        pygame.draw.arc(
            surface, (35, 30, 35),
            (265, 280, 75, 65),
            3.4, 6.0, 5
        )

        # Animal details
        if "Tiger" in name:
            for x in (215, 250, 350, 385):
                pygame.draw.line(
                    surface, (35, 35, 35),
                    (x, 165), (x + 12, 200), 9
                )

        if "Panda" in name:
            pygame.draw.ellipse(surface, (30, 30, 35),
                                (225, 200, 65, 55))
            pygame.draw.ellipse(surface, (30, 30, 35),
                                (315, 200, 65, 55))

        if "Elephant" in name:
            pygame.draw.ellipse(
                surface, color,
                (270, 285, 65, 145)
            )

        if "Lion" in name:
            pygame.draw.circle(
                surface, (185, 100, 35),
                (300, 235), 158, 24
            )

    elif category in ("VEGETABLE", "FRUIT"):

        if "Carrot" in name:
            pygame.draw.polygon(
                surface, color,
                [(230, 175), (390, 175), (310, 480)]
            )

            for x in (260, 300, 340):
                pygame.draw.line(
                    surface, (255, 195, 95),
                    (x, 250), (x - 15, 275), 6
                )

            for x in (270, 320, 370):
                pygame.draw.line(
                    surface, GREEN,
                    (310, 190), (x, 80), 13
                )

        elif "Tomato" in name:
            pygame.draw.circle(
                surface, color, (300, 300), 165
            )

            pygame.draw.polygon(
                surface, GREEN,
                [(300, 155), (270, 100),
                 (300, 130), (345, 100),
                 (330, 160), (380, 180),
                 (320, 180)]
            )

        elif "Broccoli" in name:
            pygame.draw.rect(
                surface, (115, 180, 85),
                (275, 320, 55, 180)
            )

            for x, y, radius in [
                (230, 240, 95),
                (300, 180, 115),
                (370, 245, 95),
                (300, 290, 105)
            ]:
                pygame.draw.circle(
                    surface, color, (x, y), radius
                )

        elif "Eggplant" in name:
            pygame.draw.ellipse(
                surface, color,
                (190, 190, 240, 300)
            )

            pygame.draw.polygon(
                surface, GREEN,
                [(300, 200), (250, 130),
                 (300, 150), (365, 125),
                 (340, 210)]
            )

        elif "Banana" in name:
            pygame.draw.arc(
                surface, color,
                (140, 110, 340, 400),
                0.4, 2.8, 65
            )

        elif "Watermelon" in name:
            pygame.draw.circle(
                surface, color, (300, 300), 170
            )

            pygame.draw.circle(
                surface, (245, 90, 110), (300, 300), 140
            )

            for x, y in [(250, 250), (330, 275),
                         (280, 345), (365, 350)]:
                pygame.draw.ellipse(
                    surface, (35, 45, 40),
                    (x, y, 12, 24)
                )

        else:
            pygame.draw.circle(
                surface, color, (300, 300), 155
            )

            pygame.draw.ellipse(
                surface, (255, 200, 100),
                (220, 200, 160, 200)
            )

    else:

        if "Rocket" in name:
            pygame.draw.polygon(
                surface, (220, 225, 245),
                [(300, 90), (405, 360), (195, 360)]
            )

            pygame.draw.circle(
                surface, CYAN, (300, 235), 43
            )

            pygame.draw.polygon(
                surface, RED,
                [(195, 330), (130, 440), (240, 380)]
            )

            pygame.draw.polygon(
                surface, RED,
                [(405, 330), (470, 440), (360, 380)]
            )

            pygame.draw.polygon(
                surface, ORANGE,
                [(260, 360), (340, 360), (300, 520)]
            )

        elif "Planet" in name:
            pygame.draw.circle(
                surface, color, (300, 280), 150
            )

            pygame.draw.ellipse(
                surface, (230, 185, 120),
                (115, 250, 370, 100), 16
            )

        elif "Castle" in name:
            pygame.draw.rect(
                surface, color,
                (160, 245, 280, 240)
            )

            for x in (160, 260, 340, 390):
                pygame.draw.rect(
                    surface, color,
                    (x, 170, 65, 110)
                )

                pygame.draw.polygon(
                    surface, (245, 170, 100),
                    [(x - 8, 170), (x + 32, 100),
                     (x + 73, 170)]
                )

            pygame.draw.rect(
                surface, (70, 45, 65),
                (265, 350, 70, 135)
            )

        elif "Chest" in name:
            pygame.draw.rect(
                surface, (155, 90, 35),
                (155, 250, 290, 210),
                border_radius=20
            )

            pygame.draw.rect(
                surface, (225, 165, 55),
                (155, 250, 290, 90),
                border_radius=20
            )

            pygame.draw.rect(
                surface, (255, 210, 70),
                (270, 330, 60, 75)
            )

        else:
            pygame.draw.circle(
                surface, color, (300, 300), 150
            )

    # Decorative frame
    pygame.draw.rect(
        surface, (255, 255, 255),
        (10, 10, 580, 580), 3,
        border_radius=20
    )

    return surface


# ==========================================
# GAME VARIABLES
# ==========================================

level = 1
score = 0
hints = 3
mistakes = 0

category = ""
puzzle_name = ""
art = None

grid = 3
tile_size = BOARD_SIZE // grid

tiles = []
dragging = None
drag_pos = None

completed = False
next_time = 0

# ==========================================
# CREATE LEVEL
# ==========================================

def create_level():
    global category, puzzle_name, art
    global grid, tile_size, tiles
    global hints, mistakes, dragging, completed

    category, puzzle_name, base_color = PUZZLES[
        (level - 1) % len(PUZZLES)
    ]

    grid = min(3 + (level - 1) // 4, 5)
    tile_size = BOARD_SIZE // grid

    art = make_art(category, puzzle_name, base_color)

    tiles = list(range(grid * grid))

    random.shuffle(tiles)

    # Make sure the puzzle isn't already solved
    if tiles == list(range(grid * grid)):
        tiles.reverse()

    hints = 3
    mistakes = 0
    dragging = None
    completed = False


def tile_surface(tile_number):
    row = tile_number // grid
    col = tile_number % grid

    x = col * 600 // grid
    y = row * 600 // grid

    w = (col + 1) * 600 // grid - x
    h = (row + 1) * 600 // grid - y

    return art.subsurface((x, y, w, h)).copy()


def check_win():
    return tiles == list(range(grid * grid))


# ==========================================
# HINT SYSTEM
# ==========================================

def use_hint():
    global hints, score

    if hints <= 0 or completed:
        return

    # Find first incorrect position
    for pos in range(len(tiles)):

        if tiles[pos] != pos:

            other = tiles.index(pos)

            tiles[pos], tiles[other] = (
                tiles[other], tiles[pos]
            )

            hints -= 1
            score += 10
            return


# ==========================================
# DRAW BOARD
# ==========================================

def draw_board():
    panel(
        (BOARD_X - 10, BOARD_Y - 10,
         BOARD_SIZE + 20, BOARD_SIZE + 20)
    )

    for pos, tile in enumerate(tiles):

        if dragging == pos:
            continue

        row = pos // grid
        col = pos % grid

        x = BOARD_X + col * tile_size
        y = BOARD_Y + row * tile_size

        img = tile_surface(tile)

        img = pygame.transform.smoothscale(
            img, (tile_size, tile_size)
        )

        screen.blit(img, (x, y))

        pygame.draw.rect(
            screen, (220, 230, 255),
            (x, y, tile_size, tile_size),
            2
        )

        # Tile number
        pygame.draw.circle(
            screen, (15, 25, 40),
            (x + 17, y + 17), 13
        )

        text(
            tile + 1,
            SMALL,
            WHITE,
            x + 17,
            y + 17,
            True
        )

    # Dragged tile
    if dragging is not None and drag_pos is not None:

        img = tile_surface(tiles[dragging])

        img = pygame.transform.smoothscale(
            img, (tile_size, tile_size)
        )

        screen.blit(
            img,
            (drag_pos[0] - tile_size // 2,
             drag_pos[1] - tile_size // 2)
        )


# ==========================================
# DRAW INTERFACE
# ==========================================

def draw_header():
    text("PUZZLE", BIG, WHITE, 65, 35)
    text("WORLD", BIG, CYAN, 225, 35)

    text(
        "ULTIMATE PUZZLE ADVENTURE",
        SMALL, MUTED, 70, 91
    )

    panel((840, 43, 245, 55), PANEL2)

    text(
        "★  LEVEL " + str(level),
        FONT, ORANGE, 865, 59
    )

    pygame.draw.line(
        screen, PANEL2,
        (65, 125), (1085, 125), 2
    )


def draw_sidebar():
    panel((600, 175, 485, 555))

    text(
        "PUZZLE DETAILS",
        MEDIUM, WHITE, 630, 195
    )

    text(
        category,
        SMALL, CYAN, 635, 250
    )

    text(
        puzzle_name,
        BIG, WHITE, 630, 275
    )

    # Reference image
    pygame.draw.rect(
        screen, (70, 90, 125),
        (PREVIEW_X - 5, PREVIEW_Y - 5,
         PREVIEW_SIZE + 10, PREVIEW_SIZE + 10),
        border_radius=15
    )

    preview = pygame.transform.smoothscale(
        art, (PREVIEW_SIZE, PREVIEW_SIZE)
    )

    screen.blit(preview, (PREVIEW_X, PREVIEW_Y))

    text(
        "REFERENCE IMAGE",
        SMALL, MUTED, PREVIEW_X, 540
    )

    # Statistics
    panel((630, 575, 200, 65), PANEL2)
    panel((850, 575, 200, 65), PANEL2)

    text("HINTS LEFT", SMALL, MUTED, 645, 584)
    text(hints, MEDIUM, GREEN, 645, 605)

    text("SCORE", SMALL, MUTED, 865, 584)
    text(score, MEDIUM, ORANGE, 865, 605)

    # Buttons
    button(
        "USE HINT",
        (630, 665, 195, 45),
        (55, 125, 115)
    )

    button(
        "RESTART",
        (845, 665, 205, 45),
        (100, 75, 155)
    )


def draw_footer():
    text(
        "DRAG A TILE AND DROP IT INTO ANOTHER POSITION",
        SMALL, MUTED, 65, 700
    )

    text(
        f"PIECES: {grid * grid}     |     MISTAKES: {mistakes}",
        SMALL, CYAN, 65, 730
    )


# ==========================================
# WIN ANIMATION
# ==========================================

def draw_win():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 10, 25, 190))
    screen.blit(overlay, (0, 0))

    panel((300, 270, 550, 250), PANEL2, 25)

    text(
        "PUZZLE SOLVED!",
        BIG, GREEN, WIDTH // 2, 330, True
    )

    text(
        "Amazing! Your next adventure is ready.",
        FONT, WHITE, WIDTH // 2, 395, True
    )

    text(
        "NEXT LEVEL UNLOCKING...",
        SMALL, CYAN, WIDTH // 2, 455, True
    )


# ==========================================
# START FIRST LEVEL
# ==========================================

create_level()

# ==========================================
# MAIN GAME LOOP
# ==========================================

running = True

while running:

    clock.tick(FPS)

    draw_background()
    draw_header()
    draw_board()
    draw_sidebar()
    draw_footer()

    if completed:
        draw_win()

        if pygame.time.get_ticks() >= next_time:
            level += 1
            score += 100
            create_level()

    pygame.display.flip()

    # ======================================
    # EVENTS
    # ======================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_h and not completed:
                use_hint()

            if event.key == pygame.K_r and not completed:
                create_level()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and not completed:

                mx, my = event.pos

                # Hint button
                if pygame.Rect(
                    630, 665, 195, 45
                ).collidepoint(mx, my):

                    use_hint()
                    continue

                # Restart button
                if pygame.Rect(
                    845, 665, 205, 45
                ).collidepoint(mx, my):

                    create_level()
                    continue

                # Select puzzle tile
                if (
                    BOARD_X <= mx < BOARD_X + BOARD_SIZE
                    and
                    BOARD_Y <= my < BOARD_Y + BOARD_SIZE
                ):

                    col = (mx - BOARD_X) // tile_size
                    row = (my - BOARD_Y) // tile_size

                    dragging = row * grid + col
                    drag_pos = (mx, my)

        if event.type == pygame.MOUSEMOTION:

            if dragging is not None:
                drag_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1 and dragging is not None:

                mx, my = event.pos

                if (
                    BOARD_X <= mx < BOARD_X + BOARD_SIZE
                    and
                    BOARD_Y <= my < BOARD_Y + BOARD_SIZE
                ):

                    col = (mx - BOARD_X) // tile_size
                    row = (my - BOARD_Y) // tile_size

                    target = row * grid + col

                    if target != dragging:

                        tiles[dragging], tiles[target] = (
                            tiles[target], tiles[dragging]
                        )

                        if tiles[target] != target:
                            mistakes += 1

                        if check_win():
                            completed = True
                            next_time = pygame.time.get_ticks() + 1800

                dragging = None
                drag_pos = None


pygame.quit()
sys.exit()
