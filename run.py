import pygame
import sys
import snake_easy_level
import snake_medium_level
import snake_hard_level
import gspread
from google.oauth2.service_account import Credentials
import time

pygame.init()

# Set up the screen
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Snake Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GREEN = (217, 241, 186)
GREEN = (43, 137, 58)
BLUE = (12, 44, 92)
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("slithering_challenge")
# Fonts
font = pygame.font.Font(None, 30)

# Game states
STATE_MENU = 0
STATE_LEVELS = 1
STATE_INSTRUCTIONS = 2
STATE_LEADERBOARD_MENU = 3
STATE_LEADERBOARD_EASY = 4
STATE_LEADERBOARD_MEDIUM = 5
STATE_LEADERBOARD_HARD = 6

# Current game state
current_state = STATE_MENU

# Calculate the center position of the screen
screen_center_x = screen.get_width() // 2
screen_center_y = screen.get_height() // 2

# Snake Game Heading
game_heading = font.render("Slithering challenge", True, BLUE)
game_heading_rect = game_heading.get_rect(center=(screen_center_x, 100))

# Buttons
centered_start_button = pygame.Rect(
    screen_center_x - 100, screen_center_y - 40, 200, 50
)
centered_instructions_button = pygame.Rect(
    screen_center_x - 100, screen_center_y + 30, 200, 50
)
centered_leaderboard_button = pygame.Rect(
    screen_center_x - 100, screen_center_y + 100, 200, 50
)

# Levels buttons
easy_button = pygame.Rect(screen_center_x - 100, screen_center_y - 70, 200, 50)
medium_button = pygame.Rect(screen_center_x - 100, screen_center_y - 0, 200, 50)
hard_button = pygame.Rect(screen_center_x - 100, screen_center_y + 70, 200, 50)


# Level functions
def start_easy_level():
    global current_state
    current_state = STATE_LEVELS
    pygame.display.set_caption("Snake Game - Easy Level")
    snake_easy_level.main()


def start_medium_level():
    global current_state
    current_state = STATE_LEVELS
    pygame.display.set_caption("Snake Game - Medium Level")
    snake_medium_level.main()


def start_hard_level():
    global current_state
    current_state = STATE_LEVELS
    pygame.display.set_caption("Snake Game - Hard Level")
    snake_hard_level.main()


def display_instructions():
    instructions_text = font.render("Instructions", True, BLUE)
    instruction_lines = [
        "Welcome to Snake Game!",
        "Use the arrow keys to control the snake's movement.",
        "Collect the red food to increase your score.",
        "Be careful not to run into the walls or your own body!",
        "You have three lives. Losing all lives will end the game.",
        "Press 'Esc' to pause the game at any time.",
        "After the game is over, you can choose to save your score.",
        "Press 'Yes' to save your score and see the leaderboard.",
        "Press 'No' to return to the level selection screen.",
    ]

    screen.fill(LIGHT_GREEN)

    # Center align the instructions heading
    instructions_heading_rect = instructions_text.get_rect(center=(screen_center_x, 40))
    screen.blit(instructions_text, instructions_heading_rect)

    y_position = 80  # Adjust vertical position
    for line in instruction_lines:
        instruction_render = font.render(line, True, BLUE)
        screen.blit(instruction_render, (10, y_position))
        y_position += 30  # Adjust spacing

    pygame.display.flip()


# Initialize the current leaderboard level state
current_leaderboard_state = None
sorted_easy_data = None
sorted_medium_data = None
sorted_hard_data = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if current_state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if centered_start_button.collidepoint(event.pos):
                    current_state = STATE_LEVELS

                if centered_instructions_button.collidepoint(event.pos):
                    current_state = STATE_INSTRUCTIONS

                if centered_leaderboard_button.collidepoint(event.pos):
                    current_state = STATE_LEADERBOARD_MENU

            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

        elif current_state == STATE_LEVELS:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    start_easy_level()

                if medium_button.collidepoint(event.pos):
                    start_medium_level()

                if hard_button.collidepoint(event.pos):
                    start_hard_level()

        elif current_state == STATE_INSTRUCTIONS:
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_state = STATE_MENU

        elif current_state == STATE_LEADERBOARD_MENU:
            # Draw the leaderboard menu and buttons here
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    current_leaderboard_state = STATE_LEADERBOARD_EASY
                    # Fetch and populate sorted_easy_data here
                    easy_data = SHEET.worksheet("easy").get_all_values()
                    sorted_easy_data = sorted(
                        easy_data[1:], key=lambda x: int(x[1]), reverse=True
                    )

                if medium_button.collidepoint(event.pos):
                    current_leaderboard_state = STATE_LEADERBOARD_MEDIUM
                    # Fetch and populate sorted_medium_data here
                    medium_data = SHEET.worksheet("medium").get_all_values()
                    sorted_medium_data = sorted(
                        medium_data[1:], key=lambda x: int(x[1]), reverse=True
                    )

                if hard_button.collidepoint(event.pos):
                    current_leaderboard_state = STATE_LEADERBOARD_HARD
                    # Fetch and populate sorted_hard_data here
                    hard_data = SHEET.worksheet("hard").get_all_values()
                    sorted_hard_data = sorted(
                        hard_data[1:], key=lambda x: int(x[1]), reverse=True
                    )
    # Clear the screen
    screen.fill(LIGHT_GREEN)

    if current_state == STATE_MENU:
        # Draw Snake Game Heading
        screen.blit(game_heading, game_heading_rect)

        # Draw buttons
        pygame.draw.rect(screen, GREEN, centered_start_button)
        pygame.draw.rect(screen, GREEN, centered_instructions_button)
        pygame.draw.rect(screen, GREEN, centered_leaderboard_button)

        # Draw text on buttons
        start_text = font.render("START", True, WHITE)
        instructions_text = font.render("INSTRUCTIONS", True, WHITE)
        leaderboard_text = font.render("LEADERBOARD", True, WHITE)

        screen.blit(
            start_text, start_text.get_rect(center=centered_start_button.center)
        )
        screen.blit(
            instructions_text,
            instructions_text.get_rect(center=centered_instructions_button.center),
        )
        screen.blit(
            leaderboard_text,
            leaderboard_text.get_rect(center=centered_leaderboard_button.center),
        )

    elif current_state == STATE_LEVELS:
        # Draw Levels heading
        levels_heading = font.render("Levels", True, BLUE)
        levels_heading_rect = levels_heading.get_rect(center=(screen_center_x, 100))
        screen.blit(levels_heading, levels_heading_rect)

        # Draw level buttons
        pygame.draw.rect(screen, GREEN, easy_button)
        pygame.draw.rect(screen, GREEN, medium_button)
        pygame.draw.rect(screen, GREEN, hard_button)

        # Draw text on level buttons
        easy_text = font.render("Easy", True, WHITE)
        medium_text = font.render("Medium", True, WHITE)
        hard_text = font.render("Hard", True, WHITE)

        screen.blit(easy_text, (easy_button.x + 50, easy_button.y + 10))
        screen.blit(medium_text, (medium_button.x + 20, medium_button.y + 10))
        screen.blit(hard_text, (hard_button.x + 50, hard_button.y + 10))

    elif current_state == STATE_INSTRUCTIONS:
        display_instructions()

    elif current_state == STATE_LEADERBOARD_MENU:
        # Draw the leaderboard menu
        leaderboard_menu_heading = font.render(
            "Which level toppers do you want to see?", True, BLACK
        )
        leaderboard_menu_heading_rect = leaderboard_menu_heading.get_rect(
            center=(screen_center_x, 40)
        )
        screen.blit(leaderboard_menu_heading, leaderboard_menu_heading_rect)

        # Draw level buttons
        pygame.draw.rect(screen, GREEN, easy_button)
        pygame.draw.rect(screen, GREEN, medium_button)
        pygame.draw.rect(screen, GREEN, hard_button)

        # Draw text on level buttons
        easy_text = font.render("Easy", True, WHITE)
        medium_text = font.render("Medium", True, WHITE)
        hard_text = font.render("Hard", True, WHITE)

        screen.blit(easy_text, (easy_button.x + 50, easy_button.y + 10))
        screen.blit(medium_text, (medium_button.x + 20, medium_button.y + 10))
        screen.blit(hard_text, (hard_button.x + 50, hard_button.y + 10))

        if current_leaderboard_state == STATE_LEADERBOARD_EASY and sorted_easy_data:
            y_position = 150
            for entry in sorted_easy_data:
                name_text = font.render(entry[0], True, BLACK)
                score_text = font.render(entry[1], True, BLACK)
                screen.blit(name_text, (screen_center_x - 100, y_position))
                screen.blit(score_text, (screen_center_x + 100, y_position))
                y_position += 30

        elif (
            current_leaderboard_state == STATE_LEADERBOARD_MEDIUM and sorted_medium_data
        ):
            y_position = 150
            for entry in sorted_medium_data:
                name_text = font.render(entry[0], True, BLACK)
                score_text = font.render(entry[1], True, BLACK)
                screen.blit(name_text, (screen_center_x - 100, y_position))
                screen.blit(score_text, (screen_center_x + 100, y_position))
                y_position += 30

        elif current_leaderboard_state == STATE_LEADERBOARD_HARD and sorted_hard_data:
            y_position = 150
            for entry in sorted_hard_data:
                name_text = font.render(entry[0], True, BLACK)
                score_text = font.render(entry[1], True, BLACK)
                screen.blit(name_text, (screen_center_x - 100, y_position))
                screen.blit(score_text, (screen_center_x + 100, y_position))
                y_position += 30

    pygame.display.flip()
