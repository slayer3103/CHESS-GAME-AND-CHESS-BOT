# difficulty_selection.py

import pygame
from config import WIDTH, HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)

class Button:
    def __init__(self, rect, text, font, bg_color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 3)
        label = self.font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_difficulty_selection(win):
    win.fill((30, 30, 30))

    title_font = pygame.font.SysFont(None, 48)
    button_font = pygame.font.SysFont(None, 36)

    # Title
    title = title_font.render("Choose Difficulty Level", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 5))
    win.blit(title, title_rect)

    # Define buttons
    button_width = 180
    button_height = 60
    spacing = 40
    start_y = HEIGHT // 2 - button_height

    easy_button = Button(
        (WIDTH // 2 - button_width // 2, start_y, button_width, button_height),
        "Easy", button_font
    )
    medium_button = Button(
        (WIDTH // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height),
        "Medium", button_font
    )
    hard_button = Button(
        (WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + spacing), button_width, button_height),
        "Hard", button_font
    )
    back_button = Button((20, HEIGHT - 70, 120, 50), "Back", button_font)

    # Draw all buttons
    for button in [easy_button, medium_button, hard_button, back_button]:
        button.draw(win)

    pygame.display.update()

def choose_difficulty(event):
    button_width = 180
    button_height = 60
    spacing = 40
    start_y = HEIGHT // 2 - button_height

    easy_rect = pygame.Rect(
        WIDTH // 2 - button_width // 2, start_y, button_width, button_height
    )
    medium_rect = pygame.Rect(
        WIDTH // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height
    )
    hard_rect = pygame.Rect(
        WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + spacing), button_width, button_height
    )
    back_rect = pygame.Rect((20, HEIGHT - 70, 120, 50))

    if event.type == pygame.QUIT:
        return "quit", None
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos
        if easy_rect.collidepoint(pos):
            return "game", "easy"
        
        elif medium_rect.collidepoint(pos):
            return "game","medium"
        
        elif hard_rect.collidepoint(pos):
            return "game","hard"
        
        elif back_rect.collidepoint(pos):
            return "choose_opponent", None

    return "difficulty", None
