
import pygame
import random
import sys
import math
import time

pygame.init()

# ---------------- CONFIGURATION ----------------

WIDTH, HEIGHT = 1150, 800
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUDOKU - Ultimate Edition")

clock = pygame.time.Clock()

# COLORS
BG = (12, 16, 29)
PANEL = (21, 28, 46)
PANEL2 = (28, 37, 59)
WHITE = (240, 245, 255)
MUTED = (135, 150, 180)
CYAN = (55, 220, 230)
BLUE = (75, 125, 255)
PURPLE = (155, 105, 255)
GREEN = (65, 220, 155)
RED = (255, 85, 105)
GRID = (65, 80, 110)
CELL = (27, 36, 56)
SELECTED = (52, 75, 115)
HIGHLIGHT = (35, 53, 78)

FONT = pygame.font.SysFont("segoeui", 22)
SMALL = pygame.font.SysFont("segoeui", 16)
MEDIUM = pygame.font.SysFont("segoeui", 28, bold=True)
BIG = pygame.font.SysFont("segoeui", 45, bold=True)
TITLE = pygame.font.SysFont("segoeui", 43, bold=True)

# BOARD
CELL_SIZE = 60
BOARD_X = 65
BOARD_Y = 165
BOARD_SIZE = CELL_SIZE * 9

# ---------------- SUDOKU ENGINE ----------------

def valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num:
            return False
        if board[i][col] == num:
            return False

    br = (row // 3) * 3
    bc = (col // 3) * 3

    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False

    return True


def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)

                for num in nums:
                    if valid(board, r, c, num):
                        board[r][c] = num

                        if solve(board):
                            return True

                        board[r][c] = 0

                return False

    return True


def generate_game(difficulty):
    board = [[0] * 9 for _ in range(9)]
    solve(board)

    solution = [row[:] for row in board]
    puzzle = [row[:] for row in board]

    removals = {
        "EASY": 35,
        "MEDIUM": 45,
        "HARD": 52
    }

    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    for r, c in positions[:removals[difficulty]]:
        puzzle[r][c] = 0

    return puzzle, solution


# ---------------- GAME VARIABLES ----------------

difficulty = "EASY"

original = []
board = []
solution = []

selected = None
notes_mode = False

notes = {}

mistakes = 0
hints = 3

start_time = time.time()
paused_time = 0
game_won = False
show_help = False

# ---------------- NEW GAME ----------------

def new_game(level=None):
    global difficulty, original, board, solution
    global selected, notes, mistakes, hints
    global start_time, game_won

    if level:
        difficulty = level

    board, solution = generate_game(difficulty)

    original = [row[:] for row in board]

    selected = None
    notes = {}

    mistakes = 0
    hints = 3

    start_time = time.time()
    game_won = False


new_game()

# ---------------- DRAWING FUNCTIONS ----------------

def draw_text(text, font, color, x, y, center=False):
    surface = font.render(str(text), True, color)

    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


def rounded_rect(surface, color, rect, radius=12, border=None):
    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )

    if border:
        pygame.draw.rect(
            surface,
            border,
            rect,
            width=1,
            border_radius=radius
        )


def draw_background():
    screen.fill(BG)

    # Decorative glowing circles
    pygame.draw.circle(screen, (20, 35, 70), (0, 0), 280)
    pygame.draw.circle(screen, (28, 25, 65), (WIDTH, HEIGHT), 260)


def draw_header():
    draw_text("SUDOKU", TITLE, WHITE, 65, 35)

    draw_text(
        "ULTIMATE EDITION",
        SMALL,
        CYAN,
        69,
        91
    )

    rounded_rect(
        screen,
        PANEL,
        (850, 42, 235, 52),
        15
    )

    draw_text(
        "●  GAME IN PROGRESS",
        SMALL,
        GREEN,
        870,
        59
    )

    pygame.draw.line(
        screen,
        GRID,
        (65, 125),
        (1085, 125),
        1
    )


# ---------------- BOARD ----------------

def draw_board():
    # Outer board panel
    rounded_rect(
        screen,
        PANEL,
        (BOARD_X - 8, BOARD_Y - 8,
         BOARD_SIZE + 16, BOARD_SIZE + 16),
        12
    )

    for r in range(9):
        for c in range(9):

            x = BOARD_X + c * CELL_SIZE
            y = BOARD_Y + r * CELL_SIZE

            value = board[r][c]

            color = CELL

            if selected:
                sr, sc = selected

                if r == sr or c == sc:
                    color = HIGHLIGHT

                if (r // 3 == sr // 3 and
                        c // 3 == sc // 3):
                    color = HIGHLIGHT

                if r == sr and c == sc:
                    color = SELECTED

                if value != 0 and value == board[sr][sc]:
                    color = (55, 75, 105)

            rounded_rect(
                screen,
                color,
                (x + 1, y + 1,
                 CELL_SIZE - 2, CELL_SIZE - 2),
                3
            )

            if value != 0:
                if original[r][c] != 0:
                    text_color = WHITE
                else:
                    text_color = CYAN

                if selected and value == board[selected[0]][selected[1]]:
                    text_color = GREEN

                draw_text(
                    value,
                    MEDIUM,
                    text_color,
                    x + CELL_SIZE // 2,
                    y + CELL_SIZE // 2,
                    True
                )

            elif (r, c) in notes:
                for number in notes[(r, c)]:
                    nr = (number - 1) // 3
                    nc = (number - 1) % 3

                    draw_text(
                        number,
                        SMALL,
                        MUTED,
                        x + 11 + nc * 18,
                        y + 5 + nr * 17
                    )

    # Grid lines
    for i in range(10):
        thickness = 3 if i % 3 == 0 else 1

        pygame.draw.line(
            screen,
            GRID,
            (BOARD_X + i * CELL_SIZE, BOARD_Y),
            (BOARD_X + i * CELL_SIZE,
             BOARD_Y + BOARD_SIZE),
            thickness
        )

        pygame.draw.line(
            screen,
            GRID,
            (BOARD_X, BOARD_Y + i * CELL_SIZE),
            (BOARD_X + BOARD_SIZE,
             BOARD_Y + i * CELL_SIZE),
            thickness
        )


# ---------------- BUTTONS ----------------

def button(text, x, y, w, h, color, action=None):
    mouse = pygame.mouse.get_pos()

    rect = pygame.Rect(x, y, w, h)

    hover = rect.collidepoint(mouse)

    draw_color = color

    if hover:
        draw_color = tuple(
            min(255, int(v * 1.2))
            for v in color
        )

    rounded_rect(
        screen,
        draw_color,
        rect,
        12
    )

    draw_text(
        text,
        FONT,
        WHITE,
        x + w // 2,
        y + h // 2,
        True
    )

    return rect


# ---------------- SIDEBAR ----------------

def draw_sidebar():
    sx = 680

    rounded_rect(
        screen,
        PANEL,
        (sx, 165, 405, 570),
        18
    )

    draw_text(
        "GAME CONTROL",
        MEDIUM,
        WHITE,
        sx + 25,
        185
    )

    draw_text(
        "Select your difficulty",
        SMALL,
        MUTED,
        sx + 25,
        230
    )

    levels = ["EASY", "MEDIUM", "HARD"]

    for i, level in enumerate(levels):
        x = sx + 22 + i * 122
        rect = pygame.Rect(x, 260, 112, 42)

        color = BLUE if difficulty == level else PANEL2

        rounded_rect(screen, color, rect, 10)

        draw_text(
            level,
            SMALL,
            WHITE,
            x + 56,
            281,
            True
        )

    # Stats
    rounded_rect(
        screen,
        PANEL2,
        (sx + 22, 325, 170, 90),
        12
    )

    rounded_rect(
        screen,
        PANEL2,
        (sx + 210, 325, 170, 90),
        12
    )

    elapsed = int(time.time() - start_time)

    minutes = elapsed // 60
    seconds = elapsed % 60

    draw_text("TIME", SMALL, MUTED, sx + 40, 338)

    draw_text(
        f"{minutes:02}:{seconds:02}",
        MEDIUM,
        CYAN,
        sx + 40,
        362
    )

    draw_text("MISTAKES", SMALL, MUTED, sx + 225, 338)

    draw_text(
        f"{mistakes} / 3",
        MEDIUM,
        RED if mistakes else GREEN,
        sx + 225,
        362
    )

    # Number selection
    draw_text(
        "NUMBER PAD",
        FONT,
        WHITE,
        sx + 25,
        440
    )

    for i in range(9):
        x = sx + 22 + (i % 3) * 123
        y = 480 + (i // 3) * 48

        rect = pygame.Rect(x, y, 112, 40)

        rounded_rect(
            screen,
            PANEL2,
            rect,
            9
        )

        draw_text(
            i + 1,
            FONT,
            CYAN,
            x + 56,
            y + 20,
            True
        )

    # Utility buttons
    button(
        "PENCIL: " + ("ON" if notes_mode else "OFF"),
        sx + 22, 635, 170, 42,
        PURPLE if notes_mode else PANEL2
    )

    button(
        "HINT",
        sx + 210, 635, 170, 42,
        (45, 125, 105)
    )

    draw_text(
        "N = Notes    H = Hint    R = Restart",
        SMALL,
        MUTED,
        sx + 30,
        695
    )


# ---------------- GAME STATUS ----------------

def is_complete():
    for r in range(9):
        for c in range(9):
            if board[r][c] != solution[r][c]:
                return False

    return True


def place_number(num):
    global mistakes, game_won

    if selected is None or game_won:
        return

    r, c = selected

    if original[r][c] != 0:
        return

    if notes_mode:
        key = (r, c)

        if key not in notes:
            notes[key] = set()

        if num in notes[key]:
            notes[key].remove(num)
        else:
            notes[key].add(num)

        return

    if num == solution[r][c]:
        board[r][c] = num
        notes.pop((r, c), None)

        if is_complete():
            game_won = True
    else:
        mistakes += 1


def give_hint():
    global hints, game_won

    if hints <= 0 or selected is None or game_won:
        return

    r, c = selected

    if original[r][c] != 0 or board[r][c] != 0:
        return

    board[r][c] = solution[r][c]
    notes.pop((r, c), None)
    hints -= 1

    if is_complete():
        game_won = True


# ---------------- WIN SCREEN ----------------

def draw_win_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 10, 25, 210))

    screen.blit(overlay, (0, 0))

    rounded_rect(
        screen,
        PANEL,
        (325, 250, 500, 290),
        25
    )

    draw_text(
        "PUZZLE COMPLETED!",
        BIG,
        GREEN,
        WIDTH // 2,
        315,
        True
    )

    draw_text(
        "Excellent work! You solved Sudoku.",
        FONT,
        WHITE,
        WIDTH // 2,
        385,
        True
    )

    button(
        "PLAY AGAIN",
        455, 450, 240, 55,
        BLUE
    )


# ---------------- MAIN LOOP ----------------

running = True

while running:

    clock.tick(FPS)

    draw_background()
    draw_header()
    draw_board()
    draw_sidebar()

    if game_won:
        draw_win_screen()

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = event.pos

            if game_won:
                if pygame.Rect(455, 450, 240, 55).collidepoint(mx, my):
                    new_game()
                continue

            # Board selection
            if (BOARD_X <= mx < BOARD_X + BOARD_SIZE and
                    BOARD_Y <= my < BOARD_Y + BOARD_SIZE):

                c = (mx - BOARD_X) // CELL_SIZE
                r = (my - BOARD_Y) // CELL_SIZE

                selected = (r, c)

            sx = 680

            # Difficulty
            for i, level in enumerate(["EASY", "MEDIUM", "HARD"]):

                rect = pygame.Rect(
                    sx + 22 + i * 122,
                    260,
                    112,
                    42
                )

                if rect.collidepoint(mx, my):
                    new_game(level)

            # Number pad
            for i in range(9):

                x = sx + 22 + (i % 3) * 123
                y = 480 + (i // 3) * 48

                if pygame.Rect(x, y, 112, 40).collidepoint(mx, my):
                    place_number(i + 1)

            # Notes
            if pygame.Rect(sx + 22, 635, 170, 42).collidepoint(mx, my):
                notes_mode = not notes_mode

            # Hint
            if pygame.Rect(sx + 210, 635, 170, 42).collidepoint(mx, my):
                give_hint()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_n:
                notes_mode = not notes_mode

            if event.key == pygame.K_h:
                give_hint()

            if event.key == pygame.K_r:
                new_game()

            if pygame.K_1 <= event.key <= pygame.K_9:
                place_number(event.key - pygame.K_0)

            if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                if selected and not game_won:
                    r, c = selected

                    if original[r][c] == 0:
                        board[r][c] = 0
                        notes.pop((r, c), None)

            if selected and not game_won:

                r, c = selected

                if event.key == pygame.K_UP:
                    selected = (max(0, r - 1), c)

                if event.key == pygame.K_DOWN:
                    selected = (min(8, r + 1), c)

                if event.key == pygame.K_LEFT:
                    selected = (r, max(0, c - 1))

                if event.key == pygame.K_RIGHT:
                    selected = (r, min(8, c + 1))


pygame.quit()
sys.exit()
