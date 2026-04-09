import pygame
import sys
from config import WIDTH, HEIGHT
import sound

sounds= sound.load_sounds()


pygame.mixer.init()


# Global game state
game_started = False
selected_opponent = None

def set_game_status(started, opponent=None):
    global game_started, selected_opponent
    game_started = started
    selected_opponent = opponent

def get_game_status():
    return game_started, selected_opponent

# Create buttons
def get_welcome_button(win):
    width = 200
    height = 60
    center_x = win.get_width() // 2
    start_rect = pygame.Rect(center_x - width // 2, 200, width, height)
    quit_rect = pygame.Rect(center_x - width // 2, 300, width, height)
    return {
        "Start Game": start_rect,
        "Quit": quit_rect
    }

# Draw welcome screen with background and buttons
def draw_welcome_screen(win, buttons):
    background = pygame.image.load("assets/backgrounds/bg_1.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    win.blit(background, (0, 0))
    
    # Draw title
    font = pygame.font.SysFont("Arial", 48, bold=True)
    title = font.render("Welcome to Chess Game!", True, (255, 255, 255))
    win.blit(title, (win.get_width() // 2 - title.get_width() // 2, 60))
    
    # Draw buttons
    button_font = pygame.font.SysFont("Arial", 32)
    for text, rect in buttons.items():
        pygame.draw.rect(win, (0, 0, 0), rect)
        pygame.draw.rect(win, (255, 255, 255), rect, 3)
        label = button_font.render(text, True, (255, 255, 255))
        win.blit(label, (
            rect.centerx - label.get_width() // 2,
            rect.centery - label.get_height() // 2
        ))

# Handle button events
def handle_welcome_events(event,buttons):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
        
    elif event.type == pygame.MOUSEBUTTONDOWN:
        print("Mouse clicked at:", event.pos)

        if buttons["Start Game"].collidepoint(event.pos):
            print("Start Game clicked!") 
            sound.play_sound('click', sounds)
            return "start"
        
        elif buttons["Quit"].collidepoint(event.pos):
            print("Quit clicked!")
            sound.play_sound('click', sounds)
            return "quit"

    return "welcome"
