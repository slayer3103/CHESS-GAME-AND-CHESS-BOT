import pygame
from config import WIDTH,HEIGHT
import sound 

sounds= sound.load_sounds()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
difficulty_selected = None

# Button class for reuse
class Button:
    def __init__(self, rect, text, font, bg_color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 3)  # Border
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_choose_opponent(win):
    background = pygame.image.load("assets/backgrounds/bg_2.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    win.blit(background, (0, 0))

    width, height = win.get_size()

    # Fonts
    title_font = pygame.font.SysFont(None, 48)
    button_font = pygame.font.SysFont(None, 36)

    # Title text
    title_text = title_font.render("Choose an opponent to play against", True, WHITE)
    title_rect = title_text.get_rect(center=(width // 2, height // 3))
    win.blit(title_text, title_rect)

    # Buttons
    button_width = 200
    button_height = 60
    spacing = 50
    total_width = button_width * 2 + spacing
    start_x = (width - total_width) // 2
    y_pos = height // 2

    human_button = Button((start_x, y_pos, button_width, button_height), "Human", button_font)
    computer_button = Button((start_x + button_width + spacing, y_pos, button_width, button_height), "Computer", button_font)

    back_button_y = y_pos + button_height + 40
    back_button_x = (start_x + (total_width - button_width) // 2)
    back_button = Button((back_button_x, back_button_y, button_width, button_height), "Back", button_font)

    human_button.draw(win)
    computer_button.draw(win)
    back_button.draw(win)

    pygame.display.update()

def handle_choice_events(event):
   
    button_width = 200
    button_height = 60
    spacing = 50
    total_width = button_width * 2 + spacing
    start_x = (WIDTH - total_width) // 2
    y_pos = HEIGHT // 2

    human_rect = pygame.Rect((start_x, y_pos, button_width, button_height))
    computer_rect = pygame.Rect((start_x + button_width + spacing, y_pos, button_width, button_height))
    back_button_y = y_pos + button_height + 40
    back_button_x = (start_x + (total_width - button_width) // 2)
    back_rect = pygame.Rect((back_button_x, back_button_y, button_width, button_height))

    
    if event.type == pygame.QUIT:
        return "quit", None
    
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        print("Clicked at: screen", event.pos)
        pos = event.pos
        
        if human_rect.collidepoint(pos):
            print("Clicked at:  pvp", event.pos)
            sound.play_sound('click', sounds)
            return "game", "human"
        
        elif computer_rect.collidepoint(pos):
            print("Clicked at: pvc", event.pos)
            sound.play_sound('click', sounds)
            return "game", "computer"
        
        elif back_rect.collidepoint(pos):
            print("Clicked at: back.", event.pos)
            sound.play_sound('promotion', sounds)
            return "welcome", None
        
    return "choose_opponent", None
