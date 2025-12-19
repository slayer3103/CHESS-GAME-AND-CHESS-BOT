# main.py

import pygame
import sound
from config import WIDTH, HEIGHT
from welcome_screen import (
    draw_welcome_screen, handle_welcome_events,
    get_welcome_button, set_game_status
)
from choose_opponent import draw_choose_opponent, handle_choice_events
from difficulty_selection import draw_difficulty_selection, choose_difficulty
from game_screen import main as run_game_screen

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
sounds = sound.load_sounds()

# Screen states
WELCOME, CHOOSE_OPPONENT, DIFFICULTY, GAME = (
    "welcome", "choose_opponent", "difficulty", "game"
)
current_screen = WELCOME
selected_opponent = None
selected_difficulty = None
running = True

while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # WELCOME
        if current_screen == WELCOME:
            buttons = get_welcome_button(win)
            action = handle_welcome_events(event, buttons)
            if action == "start":
                sound.play_sound('click', sounds)
                current_screen = CHOOSE_OPPONENT
            elif action == "quit":
                running = False

        # CHOOSE_OPPONENT
        elif current_screen == CHOOSE_OPPONENT:
            action, opponent = handle_choice_events(event)
            if action == "game" and opponent == "human":
                set_game_status(True, "human")
                sound.play_sound('click', sounds)
                current_screen = GAME
                run_game_screen("human", None)
            elif action == "game" and opponent == "computer":
                sound.play_sound('click', sounds)
                current_screen = DIFFICULTY
                selected_opponent = "computer"
            elif action == "welcome":
                current_screen = WELCOME

        # DIFFICULTY
        elif current_screen == DIFFICULTY:
            draw_difficulty_selection(win)
            action, difficulty = choose_difficulty(event)
            
            if action == "game" and difficulty in ("easy", "medium", "hard"):
                set_game_status(True, "computer")
                sound.play_sound('click', sounds)
                print(f"{difficulty} mode clicked")
                current_screen = GAME
                run_game_screen("computer", difficulty)
            elif action == "choose_opponent":
                current_screen = CHOOSE_OPPONENT
                print("back button clicked")

    # DRAWING
    if current_screen == WELCOME:
        buttons = get_welcome_button(win)
        draw_welcome_screen(win, buttons)
    elif current_screen == CHOOSE_OPPONENT:
        draw_choose_opponent(win)
    elif current_screen == DIFFICULTY:
        draw_difficulty_selection(win)

    pygame.display.flip()

pygame.quit()
