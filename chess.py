
import pygame
import chess
import random
import math
import sys
from pygame import gfxdraw

pygame.init()

# ==========================================
# GLASS MARBLE CHESS - PREMIUM EDITION
# ==========================================

WIDTH, HEIGHT = 1600, 1000
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.RESIZABLE
)
pygame.display.set_caption("GLASS MARBLE CHESS | Premium Edition")

clock = pygame.time.Clock()

# Colors
BG = (12, 19, 30)
PANEL = (22, 32, 47)
GOLD = (224, 185, 112)
WHITE = (245, 242, 231)
BLACK = (25, 34, 49)
GREEN = (80, 210, 155)
BLUE = (90, 170, 245)
RED = (235, 90, 100)

# Fonts
def get_font(size, bold=False):
    return pygame.font.SysFont(
        ["segoeuisymbol", "arial", "dejavusans"],
        size, bold=bold
    )

FONT = get_font(23)
SMALL = get_font(17)
TITLE = get_font(48, True)
PIECE_FONT = get_font(72)
BIG = get_font(30, True)

# Chess symbols
SYMBOLS = {
    "K": "♔", "Q": "♕", "R": "♖",
    "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜",
    "b": "♝", "n": "♞", "p": "♟"
}

# Board settings
BOARD_SIZE = 760
SQ = BOARD_SIZE // 8
BOARD_X = 55
BOARD_Y = 125

# Game state
board = chess.Board()
selected = None
legal_moves = []
history = []
move_text = []

mode = None
difficulty = 2
ai_thinking = False
winner_message = ""
last_move = None

# ==========================================
# DRAWING UTILITIES
# ==========================================

def draw_text(surface, text, font, color, x, y,
              center=False):
    img = font.render(str(text), True, color)
    rect = img.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(img, rect)
    return rect


def gradient_rect(surface, rect, top, bottom,
                  vertical=True):
    x, y, w, h = rect

    steps = h if vertical else w

    for i in range(steps):
        t = i / max(steps - 1, 1)

        color = tuple(
            int(top[j] * (1-t) + bottom[j] * t)
            for j in range(3)
        )

        if vertical:
            pygame.draw.line(
                surface, color,
                (x, y+i), (x+w, y+i)
            )
        else:
            pygame.draw.line(
                surface, color,
                (x+i, y), (x+i, y+h)
            )


def draw_panel(surface, rect, color=PANEL):
    pygame.draw.rect(
        surface, color, rect,
        border_radius=20
    )
    pygame.draw.rect(
        surface, (65, 82, 105), rect,
        2, border_radius=20
    )


def draw_button(surface, rect, text,
                mouse, active=False):
    hovered = rect.collidepoint(mouse)

    color = (48, 75, 102) if hovered else (31, 47, 67)

    if active:
        color = (61, 106, 112)

    pygame.draw.rect(
        surface, color, rect,
        border_radius=13
    )

    pygame.draw.rect(
        surface, GOLD if active else (74, 94, 117),
        rect, 2, border_radius=13
    )

    draw_text(
        surface, text, FONT, WHITE,
        rect.centerx, rect.centery, True
    )

    return hovered


# ==========================================
# GLASS MARBLE PIECES
# ==========================================

def draw_marble(surface, center, radius, piece):
    x, y = center

    is_white = piece.isupper()

    if is_white:
        base = (185, 225, 247)
        dark = (55, 112, 165)
        symbol_color = (240, 250, 255)
        outline = (110, 190, 230)
    else:
        base = (91, 103, 145)
        dark = (18, 25, 51)
        symbol_color = (220, 225, 255)
        outline = (120, 139, 190)

    # Shadow
    shadow = pygame.Surface(
        (radius*3, radius*3), pygame.SRCALPHA
    )

    pygame.draw.circle(
        shadow, (0, 0, 0, 100),
        (radius*1.5, radius*1.6),
        radius
    )

    surface.blit(
        shadow, (x-radius*1.5+5, y-radius*1.5+8)
    )

    # Main marble
    gfxdraw.filled_circle(
        surface, x, y, radius, dark
    )

    gfxdraw.filled_circle(
        surface, x, y-radius//7,
        radius-3, base
    )

    # Gradient-like inner shading
    for i in range(radius-5, 4, -3):
        alpha = i / radius

        color = tuple(
            int(dark[j]*(1-alpha) + base[j]*alpha)
            for j in range(3)
        )

        gfxdraw.filled_circle(
            surface, x, y+radius//5,
            i, color
        )

    # Glass outline
    gfxdraw.aacircle(
        surface, x, y, radius, outline
    )

    # Reflection
    gfxdraw.filled_ellipse(
        surface,
        x-radius//3,
        y-radius//2,
        radius//3,
        max(5, radius//7),
        (240, 250, 255)
    )

    gfxdraw.filled_circle(
        surface,
        x+radius//3,
        y+radius//3,
        max(3, radius//10),
        (215, 235, 255)
    )

    # Chess symbol
    symbol = SYMBOLS[piece]

    img = PIECE_FONT.render(
        symbol, True, symbol_color
    )

    img = pygame.transform.smoothscale(
        img, (radius*2, radius*2)
    )

    img_rect = img.get_rect(center=(x, y-2))
    surface.blit(img, img_rect)


# ==========================================
# CHESS BOARD
# ==========================================

def square_center(square):
    file = chess.square_file(square)
    rank = chess.square_rank(square)

    x = BOARD_X + file*SQ + SQ//2
    y = BOARD_Y + (7-rank)*SQ + SQ//2

    return x, y


def draw_board():
    mouse = pygame.mouse.get_pos()

    # Board outer frame
    outer = pygame.Rect(
        BOARD_X-13, BOARD_Y-13,
        BOARD_SIZE+26, BOARD_SIZE+26
    )

    pygame.draw.rect(
        screen, (8, 13, 23),
        outer, border_radius=16
    )

    pygame.draw.rect(
        screen, GOLD,
        outer, 3, border_radius=16
    )

    for rank in range(8):
        for file in range(8):

            square = chess.square(file, 7-rank)

            x = BOARD_X + file*SQ
            y = BOARD_Y + rank*SQ

            rect = pygame.Rect(x, y, SQ, SQ)

            light = (213, 206, 184)
            dark = (64, 91, 111)

            color = light if (rank+file)%2 == 0 else dark

            pygame.draw.rect(screen, color, rect)

            # Selected square
            if selected == square:
                pygame.draw.rect(
                    screen, (230, 190, 75),
                    rect, 5
                )

            # Last move
            if last_move and square in (
                last_move.from_square,
                last_move.to_square
            ):
                overlay = pygame.Surface(
                    (SQ, SQ), pygame.SRCALPHA
                )
                overlay.fill((255, 220, 80, 65))
                screen.blit(overlay, (x, y))

            # Legal move indicators
            for move in legal_moves:
                if move.to_square == square:

                    if board.piece_at(square):
                        pygame.draw.circle(
                            screen, GREEN,
                            (x+SQ//2, y+SQ//2),
                            SQ//2-7, 5
                        )
                    else:
                        pygame.draw.circle(
                            screen, (36, 110, 81),
                            (x+SQ//2, y+SQ//2),
                            12
                        )

            # Piece
            piece = board.piece_at(square)

            if piece:
                draw_marble(
                    screen,
                    (x+SQ//2, y+SQ//2),
                    39,
                    piece.symbol()
                )

            # Coordinates
            if file == 0:
                draw_text(
                    screen, str(8-rank), SMALL,
                    (55, 65, 75), x+5, y+3
                )

            if rank == 7:
                draw_text(
                    screen, chr(97+file), SMALL,
                    (55, 65, 75),
                    x+SQ-20, y+SQ-24
                )


# ==========================================
# COMPUTER AI
# ==========================================

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


def evaluate_position(b):
    if b.is_checkmate():
        return -100000 if b.turn else 100000

    if b.is_game_over():
        return 0

    score = 0

    for square, piece in b.piece_map().items():

        value = PIECE_VALUES[piece.piece_type]

        file = chess.square_file(square)
        rank = chess.square_rank(square)

        # Slight central-square preference
        center_bonus = int(
            8 - (
                abs(3.5-file) + abs(3.5-rank)
            ) * 2
        )

        value += center_bonus

        if piece.color == chess.WHITE:
            score += value
        else:
            score -= value

    return score


def minimax(b, depth, alpha, beta, maximizing):
    if depth == 0 or b.is_game_over():
        return evaluate_position(b), None

    best_move = None

    moves = list(b.legal_moves)
    random.shuffle(moves)

    # Try captures first
    moves.sort(
        key=lambda m: b.is_capture(m),
        reverse=True
    )

    if maximizing:
        best_score = -math.inf

        for move in moves:
            b.push(move)

            score, _ = minimax(
                b, depth-1, alpha, beta, False
            )

            b.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

            if beta <= alpha:
                break

        return best_score, best_move

    else:
        best_score = math.inf

        for move in moves:
            b.push(move)

            score, _ = minimax(
                b, depth-1, alpha, beta, True
            )

            b.pop()

            if score < best_score:
                best_score = score
                best_move = move

            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score, best_move


def computer_move():
    global last_move, selected, legal_moves

    if board.is_game_over():
        return

    depth = difficulty

    _, move = minimax(
        board, depth,
        -math.inf, math.inf,
        board.turn == chess.WHITE
    )

    if move:
        history.append(board.fen())
        board.push(move)
        last_move = move

    selected = None
    legal_moves = []


# ==========================================
# SIDE PANEL
# ==========================================

def draw_sidebar():
    panel = pygame.Rect(875, 100, 675, 800)

    draw_panel(screen, panel)

    draw_text(
        screen, "GLASS MARBLE",
        TITLE, GOLD, 915, 135
    )

    draw_text(
        screen, "CHESS", BIG,
        WHITE, 920, 190
    )

    pygame.draw.line(
        screen, GOLD,
        (915, 245), (1510, 245), 2
    )

    # Mode
    mode_name = (
        "FRIEND MATCH" if mode == "friend"
        else "COMPUTER MATCH"
    )

    draw_text(
        screen, "GAME MODE",
        SMALL, (150, 170, 195), 920, 275
    )

    draw_text(
        screen, mode_name,
        BIG, GREEN, 920, 305
    )

    # Turn
    turn = "WHITE" if board.turn else "BLACK"

    draw_text(
        screen, "CURRENT TURN",
        SMALL, (150, 170, 195), 920, 375
    )

    draw_text(
        screen, turn,
        BIG, WHITE, 920, 410
    )

    # Status
    if board.is_checkmate():
        status = "CHECKMATE!"
    elif board.is_stalemate():
        status = "STALEMATE!"
    elif board.is_check():
        status = "CHECK!"
    elif board.is_game_over():
        status = "DRAW!"
    else:
        status = "GAME IN PROGRESS"

    draw_text(
        screen, "GAME STATUS",
        SMALL, (150, 170, 195), 920, 475
    )

    draw_text(
        screen, status,
        FONT, RED if board.is_check() else GREEN,
        920, 505
    )

    # Move history
    draw_text(
        screen, "MOVE HISTORY",
        FONT, GOLD, 920, 570
    )

    history_rect = pygame.Rect(
        915, 610, 595, 175
    )

    pygame.draw.rect(
        screen, (14, 23, 36),
        history_rect, border_radius=12
    )

    recent = move_text[-10:]

    for i, item in enumerate(recent):
        draw_text(
            screen, item, SMALL,
            WHITE, 935, 625+i*28
        )

    # Bottom buttons
    mouse = pygame.mouse.get_pos()

    global undo_rect, restart_rect, menu_rect

    undo_rect = pygame.Rect(915, 815, 175, 55)
    restart_rect = pygame.Rect(1100, 815, 190, 55)
    menu_rect = pygame.Rect(1300, 815, 210, 55)

    draw_button(screen, undo_rect, "UNDO", mouse)
    draw_button(screen, restart_rect, "RESTART", mouse)
    draw_button(screen, menu_rect, "MAIN MENU", mouse)


# ==========================================
# MENU
# ==========================================

def draw_menu():
    screen.fill(BG)

    # Background decoration
    for i in range(12):
        pygame.draw.circle(
            screen, (23, 39, 55),
            (100+i*140, 80+i%3*280),
            90, 2
        )

    draw_text(
        screen, "GLASS MARBLE CHESS",
        get_font(65, True), GOLD,
        WIDTH//2, 220, True
    )

    draw_text(
        screen, "A PREMIUM CHESS EXPERIENCE",
        FONT, (170, 190, 210),
        WIDTH//2, 290, True
    )

    # Marble decoration
    draw_marble(
        screen, (WIDTH//2, 395), 48, "K"
    )

    mouse = pygame.mouse.get_pos()

    global computer_rect, friend_rect
    global easy_rect, medium_rect, hard_rect

    computer_rect = pygame.Rect(
        WIDTH//2-220, 500, 440, 70
    )

    friend_rect = pygame.Rect(
        WIDTH//2-220, 590, 440, 70
    )

    draw_button(
        screen, computer_rect,
        "PLAY VS COMPUTER", mouse
    )

    draw_button(
        screen, friend_rect,
        "PLAY WITH FRIEND", mouse
    )

    draw_text(
        screen, "AI DIFFICULTY",
        SMALL, GOLD, WIDTH//2, 720, True
    )

    easy_rect = pygame.Rect(
        WIDTH//2-220, 750, 130, 55
    )

    medium_rect = pygame.Rect(
        WIDTH//2-65, 750, 130, 55
    )

    hard_rect = pygame.Rect(
        WIDTH//2+90, 750, 130, 55
    )

    draw_button(
        screen, easy_rect, "EASY",
        mouse, difficulty == 1
    )

    draw_button(
        screen, medium_rect, "MEDIUM",
        mouse, difficulty == 2
    )

    draw_button(
        screen, hard_rect, "HARD",
        mouse, difficulty == 3
    )

    draw_text(
        screen, "Designed for smooth high-resolution play",
        SMALL, (125, 145, 165),
        WIDTH//2, 860, True
    )


# ==========================================
# GAME CONTROL
# ==========================================

def start_game(selected_mode):
    global board, mode, selected, legal_moves
    global history, move_text, last_move

    board = chess.Board()
    mode = selected_mode

    selected = None
    legal_moves = []

    history = []
    move_text = []
    last_move = None


def undo_move():
    global selected, legal_moves, last_move

    if not history:
        return

    # In computer mode undo both computer and
    # human moves when possible.
    count = 2 if mode == "computer" and len(history) >= 2 else 1

    for _ in range(count):
        if history:
            board.set_fen(history.pop())
            if move_text:
                move_text.pop()

    last_move = board.peek() if board.move_stack else None

    selected = None
    legal_moves = []


def save_move(move):
    global last_move, selected, legal_moves

    history.append(board.fen())

    san = board.san(move)

    move_number = len(board.move_stack) // 2 + 1

    if board.turn == chess.WHITE:
        move_text.append(
            f"{move_number}. {san}"
        )
    else:
        if move_text:
            move_text[-1] += f"   {san}"
        else:
            move_text.append(
                f"{move_number}... {san}"
            )

    board.push(move)

    last_move = move
    selected = None
    legal_moves = []


def handle_board_click(pos):
    global selected, legal_moves

    x, y = pos

    if not (
        BOARD_X <= x < BOARD_X+BOARD_SIZE
        and BOARD_Y <= y < BOARD_Y+BOARD_SIZE
    ):
        return

    file = (x-BOARD_X)//SQ
    rank = 7-(y-BOARD_Y)//SQ

    square = chess.square(file, rank)

    if selected is not None:

        possible = [
            m for m in legal_moves
            if m.to_square == square
        ]

        if possible:
            move = possible[0]

            # Auto queen promotion
            if move.promotion:
                move = chess.Move(
                    move.from_square,
                    move.to_square,
                    promotion=chess.QUEEN
                )

            if move in board.legal_moves:
                save_move(move)
                return

        # Select another own piece
        piece = board.piece_at(square)

        if piece and piece.color == board.turn:
            selected = square
            legal_moves = [
                m for m in board.legal_moves
                if m.from_square == square
            ]
        else:
            selected = None
            legal_moves = []

    else:
        piece = board.piece_at(square)

        if piece and piece.color == board.turn:
            selected = square

            legal_moves = [
                m for m in board.legal_moves
                if m.from_square == square
            ]


# ==========================================
# MAIN LOOP
# ==========================================

running = True
in_menu = True

while running:

    clock.tick(60)

    mouse = pygame.mouse.get_pos()

    # Handle AI turn
    if (
        not in_menu
        and mode == "computer"
        and board.turn == chess.BLACK
        and not board.is_game_over()
    ):
        ai_thinking = True
        screen.fill(BG)
        draw_board()
        draw_sidebar()

        draw_text(
            screen, "COMPUTER THINKING...",
            BIG, GOLD, 930, 925
        )

        pygame.display.flip()

        computer_move()

        if board.move_stack:
            last_move = board.peek()

        ai_thinking = False

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = max(1200, event.w), max(850, event.h)
            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT), pygame.RESIZABLE
            )

            # Keep the game board at its designed
            # resolution for crisp drawing.
            BOARD_X = 55
            BOARD_Y = 125

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if in_menu:

                    if computer_rect.collidepoint(event.pos):
                        start_game("computer")
                        in_menu = False

                    elif friend_rect.collidepoint(event.pos):
                        start_game("friend")
                        in_menu = False

                    elif easy_rect.collidepoint(event.pos):
                        difficulty = 1

                    elif medium_rect.collidepoint(event.pos):
                        difficulty = 2

                    elif hard_rect.collidepoint(event.pos):
                        difficulty = 3

                else:

                    if undo_rect.collidepoint(event.pos):
                        undo_move()

                    elif restart_rect.collidepoint(event.pos):
                        start_game(mode)

                    elif menu_rect.collidepoint(event.pos):
                        in_menu = True

                    elif (
                        mode == "friend"
                        or board.turn == chess.WHITE
                    ):
                        handle_board_click(event.pos)

    # Draw
    screen.fill(BG)

    if in_menu:
        draw_menu()

    else:
        draw_board()
        draw_sidebar()

        if board.is_game_over():
            result = board.result()

            if result == "1-0":
                message = "WHITE WINS!"
            elif result == "0-1":
                message = "BLACK WINS!"
            else:
                message = "DRAW!"

            pygame.draw.rect(
                screen, (15, 25, 40),
                (400, 450, 350, 90),
                border_radius=15
            )

            draw_text(
                screen, message,
                BIG, GOLD, 575, 495, True
            )

    pygame.display.flip()

pygame.quit()
sys.exit()
