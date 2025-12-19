import pygame 
import sys
import chess 
import time
from config import BOARD_SIZE, SQUARE_SIZE, SIDEBAR_WIDTH, LEFTBAR_WIDTH, TOPBAR_HEIGHT, BOTTOMBAR_HEIGHT, WIDTH, HEIGHT

pygame.init()

win = pygame.display.set_mode((WIDTH, HEIGHT))


# Draw the board
def draw_game_board():
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, pygame.Rect(
                LEFTBAR_WIDTH + col * SQUARE_SIZE,
                TOPBAR_HEIGHT + row * SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE
            ))

# Draw sidebars( right and left)
def draw_sidebars(move_log, white_time, black_time):
    # Left sidebar - Timer
    pygame.draw.rect(win, (235, 235, 250), (0, 0, LEFTBAR_WIDTH, HEIGHT))
    timer_font = pygame.font.SysFont("Consolas", 20)
    win.blit(timer_font.render("Time", True, (0, 0, 0)), (5, 10))
    win.blit(timer_font.render("W:", True, (0, 0, 0)), (5, 40))
    win.blit(timer_font.render(time.strftime('%M:%S', time.gmtime(white_time)), True, (0, 0, 0)), (5, 60))
    win.blit(timer_font.render("B:", True, (0, 0, 0)), (5, 90))
    win.blit(timer_font.render(time.strftime('%M:%S', time.gmtime(black_time)), True, (0, 0, 0)), (5, 110))

    # Right sidebar - Move History
    pygame.draw.rect(win, (255, 253, 208), (LEFTBAR_WIDTH + BOARD_SIZE, 0, SIDEBAR_WIDTH, HEIGHT))
    font = pygame.font.SysFont("Arial", 18)
    title = font.render("Moves", True, (0, 0, 0))
    win.blit(title, (LEFTBAR_WIDTH + BOARD_SIZE + 10, 10))
    for i in range(0, len(move_log), 2):
        move_text = f"{i // 2 + 1}. {move_log[i]}"
        if i + 1 < len(move_log):
            move_text += f" {move_log[i + 1]}"
        text_surface = font.render(move_text, True, (0, 0, 0))
        win.blit(text_surface, (LEFTBAR_WIDTH + BOARD_SIZE + 10, 40 + (i // 2) * 20))

# drawing top bar and button
def draw_topbar(win):
    import pygame
    import sound
    from config import LEFTBAR_WIDTH, BOARD_SIZE, TOPBAR_HEIGHT

    button_font = pygame.font.SysFont("Arial", 22)
    win.fill((200, 200, 200), (0, 0, LEFTBAR_WIDTH + BOARD_SIZE, TOPBAR_HEIGHT))

    # Button layout settings
    button_width = 110
    button_height = 40
    gap = 20

    total_width = 3 * button_width + 2 * gap
    start_x = LEFTBAR_WIDTH + (BOARD_SIZE - total_width) // 2
    y = (TOPBAR_HEIGHT - button_height) // 2

    button_order = ["Mute", "Restart", "End"]
    buttons = {}

    for text in button_order:
        button_rect = pygame.Rect(start_x, y, button_width, button_height)

        if text == "Mute" and sound.is_muted():
            pygame.draw.rect(win, (200, 50, 50), button_rect)  # Red for muted
        else:
            pygame.draw.rect(win, (100, 100, 100), button_rect)  # Dark gray

        pygame.draw.rect(win, (0, 0, 0), button_rect, 2)  # Border
        text_surface = button_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        win.blit(text_surface, text_rect)

        buttons[text] = button_rect
        start_x += button_width + gap

    return buttons

# Bottombar (Text area/ msg) 
def draw_bottombar(message):
    pygame.draw.rect(win, (220, 220, 220), (0, HEIGHT - BOTTOMBAR_HEIGHT, WIDTH, BOTTOMBAR_HEIGHT))
    font = pygame.font.SysFont("Arial", 20)
    win.blit(font.render(message, True, (0, 0, 0)), (10, HEIGHT - BOTTOMBAR_HEIGHT + 10))

# Labels for ranks (1-8) and files (a-h)  ranks= height form white to black  , file = width from left to right 
def draw_labels():
    font = pygame.font.SysFont("Arial", 16)
    for i in range(8):
        # Ranks (1-8)
        text = font.render(str(8 - i), True, (0, 0, 0))
        win.blit(text, (LEFTBAR_WIDTH // 2 - text.get_width() // 2, TOPBAR_HEIGHT + i * SQUARE_SIZE + SQUARE_SIZE // 2 - 8))

        # Files (a-h)
        text = font.render(chr(ord('a') + i), True, (0, 0, 0))
        x = LEFTBAR_WIDTH + i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_width() // 2
        y = TOPBAR_HEIGHT + 8 * SQUARE_SIZE + 5
        win.blit(text, (x, y))
