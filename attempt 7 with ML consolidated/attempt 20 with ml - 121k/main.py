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

        # 1) Welcome Screen
        if current_screen == WELCOME:
            buttons = get_welcome_button(win)
            action = handle_welcome_events(event, buttons)
            if action == "start":
                sound.play_sound('click', sounds)
                current_screen = CHOOSE_OPPONENT
            elif action == "quit":
                running = False

        # 2) Choose Opponent
        elif current_screen == CHOOSE_OPPONENT:
            action, opponent = handle_choice_events(event)
            if action == "game":
                selected_opponent = opponent
                sound.play_sound('click', sounds)
                if opponent == "human":
                    set_game_status(True, "human")
                    current_screen = GAME
                else:  # computer
                    sound.play_sound('click', sounds)
                    current_screen = DIFFICULTY

            elif action == "welcome":
                current_screen = WELCOME

        # 3) Difficulty
        elif current_screen == DIFFICULTY:
            draw_difficulty_selection(win)  # immediate draw so user sees it
            action, difficulty = choose_difficulty(event)
            if action == "game":
                selected_difficulty = difficulty.lower()
                set_game_status(True, "computer")
                sound.play_sound('click', sounds)
                current_screen = GAME
            elif action == "choose_opponent":
                current_screen = CHOOSE_OPPONENT
                sound.play_sound('click', sounds)

        # 4) Game
        elif current_screen == GAME:
            # Launch the game loop exactly once, capturing its result
            result = run_game_screen(selected_opponent, selected_difficulty)
            # Handle return code
            if result == "restart":
                set_game_status(True, None)
                sound.play_sound('click', sounds)
                current_screen = CHOOSE_OPPONENT
            elif result == "end":
                set_game_status(False, None)
                sound.play_sound('click', sounds)
                current_screen = WELCOME
            else:
                running = False  # quit entirely

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
