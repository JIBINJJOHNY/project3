import pygame
import random
import sys
import gspread
from google.oauth2.service_account import Credentials

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20
BORDER_SIZE = 20
WHITE = (0, 111, 70)
GREEN = (252, 201, 35)
RED = (179, 27, 27)
BLACK = (60, 20, 33)
FONT = pygame.font.Font(None, 36)
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("slithering_challenge")
easy = SHEET.worksheet("easy")

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game - Easy Level")


# Snake class
class Snake:
    def __init__(self):
        self.positions = [(100, 100), (80, 100), (60, 100)]
        self.direction = (CELL_SIZE, 0)

    def update(self):
        self.positions.insert(
            0,
            (
                self.positions[0][0] + self.direction[0],
                self.positions[0][1] + self.direction[1],
            ),
        )
        self.positions.pop()

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, CELL_SIZE):
                    self.direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and self.direction != (0, -CELL_SIZE):
                    self.direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and self.direction != (CELL_SIZE, 0):
                    self.direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-CELL_SIZE, 0):
                    self.direction = (CELL_SIZE, 0)


# Food class
class Food:
    def __init__(self):
        self.color = RED
        self.update()

    def update(self):
        valid_positions = [
            (x, y)
            for x in range(BORDER_SIZE, SCREEN_WIDTH - BORDER_SIZE, CELL_SIZE)
            for y in range(BORDER_SIZE, SCREEN_HEIGHT - BORDER_SIZE, CELL_SIZE)
        ]
        self.position = random.choice(valid_positions)


# Function to get top scores from the Google Sheet
def get_top_scores(level):
    worksheet = SHEET.worksheet(level)
    records = worksheet.get_all_records()
    sorted_records = sorted(records, key=lambda x: x["score"], reverse=True)
    return sorted_records[:10]  # Get top 10 scores


def display_top_scores(level, user_name):
    top_scores = get_top_scores(level)
    top_scores_text = FONT.render("Top Scores:", True, BLACK)
    screen.fill(WHITE)
    screen.blit(top_scores_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 180))

    y_position = SCREEN_HEIGHT // 2 - 140
    for i, score_entry in enumerate(top_scores):
        entry_text = f"{i + 1}. {score_entry['player_name']}: {score_entry['score']}"
        if score_entry["player_name"] == user_name:
            entry_render = FONT.render(
                entry_text, True, RED
            )  # Highlight user's name in red
        else:
            entry_render = FONT.render(entry_text, True, GREEN)
        screen.blit(entry_render, (SCREEN_WIDTH // 2 - 80, y_position))
        y_position += 40

    pygame.display.flip()


# Main function
def main():
    """
    The main game loop and logic are contained within this function
    """
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food()
    lives = 3
    score = 0
    paused = False
    # Display "Level Easy" heading
    level_heading = FONT.render("Level Easy", True, BLACK)
    screen.blit(level_heading, (SCREEN_WIDTH // 2 - 80, 10))
    pygame.display.flip()

    # The core game loop that runs while the player has lives left
    while lives > 0:
        snake.handle_keys()
        snake.update()
        # Handles snake movement and collision detection with food and screen boundaries.
        if snake.positions[0] == food.position:
            score += 1
            food.update()
            snake.positions.append((0, 0))  # Grow the snake

        if snake.positions[0][0] >= SCREEN_WIDTH - BORDER_SIZE:
            snake.positions[0] = (BORDER_SIZE, snake.positions[0][1])
        elif snake.positions[0][0] < BORDER_SIZE:
            snake.positions[0] = (SCREEN_WIDTH - CELL_SIZE, snake.positions[0][1])
        if snake.positions[0][1] >= SCREEN_HEIGHT - BORDER_SIZE:
            snake.positions[0] = (snake.positions[0][0], BORDER_SIZE)
        elif snake.positions[0][1] < BORDER_SIZE:
            snake.positions[0] = (snake.positions[0][0], SCREEN_HEIGHT - CELL_SIZE)

        if snake.positions[0] in snake.positions[1:]:
            lives -= 1
            # Reset snake position
            pygame.time.delay(1000)  # Pause for a moment

        # Draw everything
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, SCREEN_WIDTH, BORDER_SIZE))
        pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, BORDER_SIZE, SCREEN_HEIGHT))
        pygame.draw.rect(
            screen,
            BLACK,
            pygame.Rect(SCREEN_WIDTH - BORDER_SIZE, 0, BORDER_SIZE, SCREEN_HEIGHT),
        )
        pygame.draw.rect(
            screen,
            BLACK,
            pygame.Rect(0, SCREEN_HEIGHT - BORDER_SIZE, SCREEN_WIDTH, BORDER_SIZE),
        )
        pygame.draw.rect(
            screen,
            GREEN,
            pygame.Rect(
                snake.positions[0][0], snake.positions[0][1], CELL_SIZE, CELL_SIZE
            ),
        )
        for segment in snake.positions[1:]:
            pygame.draw.rect(
                screen, GREEN, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE)
            )
        pygame.draw.rect(
            screen,
            food.color,
            pygame.Rect(food.position[0], food.position[1], CELL_SIZE, CELL_SIZE),
        )

        score_text = FONT.render(f"Score: {score}", True, GREEN)
        lives_text = FONT.render(f"Lives: {lives}", True, GREEN)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        pygame.display.flip()
        clock.tick(10)  # Snake speed

    screen.fill(WHITE)
    game_over_text = FONT.render("Game Over", True, RED)
    final_score_text = FONT.render(f"Final Score: {score}", True, RED)
    save_prompt = FONT.render("Do you want to save your score?", True, BLACK)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))
    screen.blit(save_prompt, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20))

    yes_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 80, 100, 40)
    no_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 130, 100, 40)

    pygame.draw.rect(screen, GREEN, yes_button)
    pygame.draw.rect(screen, RED, no_button)

    yes_text = FONT.render("Yes", True, WHITE)
    no_text = FONT.render("No", True, WHITE)

    screen.blit(yes_text, (yes_button.x + 30, yes_button.y + 10))
    screen.blit(no_text, (no_button.x + 30, no_button.y + 10))

    pygame.display.flip()

    yes_clicked = False
    no_clicked = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.collidepoint(event.pos):
                    yes_clicked = True
                elif no_button.collidepoint(event.pos):
                    import run  # Import the run module

                    run.show_level_selection()  # Call the function to show level selection

        if yes_clicked:
            # Clear the screen and prompt for player's name
            screen.fill(WHITE)
            input_prompt = FONT.render("Enter your name:", True, BLACK)
            screen.blit(
                input_prompt, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20)
            )
            pygame.display.flip()

            name = ""
            input_active = True
            name_already_used = False  # Flag to track if name is already used

            while input_active:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_RETURN:
                            if name in [
                                entry["player_name"] for entry in get_top_scores("easy")
                            ]:
                                name_already_used = True
                            else:
                                input_active = False
                        elif e.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                        else:
                            name += e.unicode

                # Clear the screen and display the input prompt
                screen.fill(WHITE)
                screen.blit(
                    input_prompt, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20)
                )
                pygame.draw.rect(
                    screen,
                    BLACK,
                    pygame.Rect(
                        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 40
                    ),
                )

                if name_already_used:
                    error_message = FONT.render(
                        "Name already in use. Try another name.", True, RED
                    )
                    screen.blit(
                        error_message,
                        (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 80),
                    )
                    name_already_used = False  # Reset the flag here
                else:
                    name_text = FONT.render(name, True, GREEN)
                    screen.blit(
                        name_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 30)
                    )

                pygame.display.flip()

            if not name_already_used:
                # Add the new score to the Google Sheets
                easy.append_row(
                    [name, score]
                )  # Append the player's name and score to the "easy" worksheet

                # Display top scores for the "easy" level
                display_top_scores("easy", name)

            # Reset name_already_used for the next input
            name_already_used = False

            # Reset yes_clicked to allow for future submissions
            yes_clicked = False

            # Reset name and input_active for the next input
            name = ""
            input_active = True

        if no_clicked:
            import run  # Import the run module

            run.show_level_selection()  # Call the function to show level selection
            break  # Exit the loop to return to the levels screen


if __name__ == "__main__":
    main()
