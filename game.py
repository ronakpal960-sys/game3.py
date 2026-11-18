
import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)

# Snake settings
snake = [[100, 100], [80, 100], [60, 100]]
direction = "RIGHT"

# Food
food = [
    random.randrange(0, WIDTH, 20),
    random.randrange(0, HEIGHT, 20)
]

score = 0
game_over = False

# Main game loop
while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP and direction != "DOWN":
                direction = "UP"

            elif event.key == pygame.K_DOWN and direction != "UP":
                direction = "DOWN"

            elif event.key == pygame.K_LEFT and direction != "RIGHT":
                direction = "LEFT"

            elif event.key == pygame.K_RIGHT and direction != "LEFT":
                direction = "RIGHT"

            if game_over and event.key == pygame.K_SPACE:
                snake = [[100, 100], [80, 100], [60, 100]]
                direction = "RIGHT"
                score = 0
                food = [
                    random.randrange(0, WIDTH, 20),
                    random.randrange(0, HEIGHT, 20)
                ]
                game_over = False

    if not game_over:

        # Move snake
        head = snake[0].copy()

        if direction == "UP":
            head[1] -= 20
        elif direction == "DOWN":
            head[1] += 20
        elif direction == "LEFT":
            head[0] -= 20
        elif direction == "RIGHT":
            head[0] += 20

        snake.insert(0, head)

        # Eat food
        if head == food:
            score += 10
            while food in snake:
                food = [
                    random.randrange(0, WIDTH, 20),
                    random.randrange(0, HEIGHT, 20)
                ]
        else:
            snake.pop()

        # Collision detection
        if (head[0] < 0 or head[0] >= WIDTH or
            head[1] < 0 or head[1] >= HEIGHT or
            head in snake[1:]):
            game_over = True

    # Draw everything
    screen.fill(BLACK)

    for part in snake:
        pygame.draw.rect(screen, GREEN, (part[0], part[1], 20, 20))

    pygame.draw.rect(screen, RED, (food[0], food[1], 20, 20))

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    if game_over:
        text = font.render("GAME OVER! Press SPACE to Restart", True, WHITE)
        screen.blit(text, (65, HEIGHT // 2))

    pygame.display.update()
    clock.tick(10)
