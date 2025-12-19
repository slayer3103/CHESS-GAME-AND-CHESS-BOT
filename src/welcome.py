import pygame
import sys
from datetime import datetime

# State variables
game_started = False
selected_opponent = None

# Colors and fonts
BG_COLOR = (245, 245, 245)
TITLE_COLOR = (40, 40, 40)
BUTTON_COLOR = (180, 180, 255)
BUTTON_HOVER = (140, 140, 220)
TEXT_COLOR = (0, 0, 0)

# Fonts initialized later in draw_welcome_screen
font_title = None
font_button = None

# Button dimensions and positions
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_SPACING = 30

buttons = []


def draw_welcome_screen(screen):
    global font_title, font_button, buttons

    if not font_title or not font_button:
        font_title = pygame.font.SysFont("arial", 64, True)
        font_button = pygame.font.SysFont("arial", 32)

    screen.fill(BG_COLOR)

    # Draw title
    title_text = font_title.render("Welcome to Chess!", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, 120))
    screen.blit(title_text, title_rect)

    # Define button positions
    center_x = screen.get_width() // 2
    start_y = 250

    labels = ["Player vs Player", "Player vs Computer"]
    buttons = []

    for i, label in enumerate(labels):
        x = center_x - BUTTON_WIDTH // 2
        y = start_y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
        rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        buttons.append((rect, label))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)

        text_surface = font_button.render(label, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    pygame.display.flip()


def handle_welcome_events():
    global game_started, selected_opponent

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            for rect, label in buttons:
                if rect.collidepoint(mouse_pos):
                    if "Player vs Player" in label:
                        selected_opponent = "human"
                    elif "Player vs Computer" in label:
                        selected_opponent = "computer"
                    game_started = True


def get_game_status():
    return game_started, selected_opponent


def reset_welcome_screen():
    global game_started, selected_opponent
    game_started = False
    selected_opponent = None
