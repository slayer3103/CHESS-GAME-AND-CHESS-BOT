import pygame

# Initialize Pygame mixer for sounds
pygame.mixer.init()

# Load sounds
def load_sounds():
    sounds = {
        'move': pygame.mixer.Sound("assets/sounds/move.wav"),
        'capture': pygame.mixer.Sound("assets/sounds/capture.wav"),
        'check': pygame.mixer.Sound("assets/sounds/check.wav"),
        'checkmate': pygame.mixer.Sound("assets/sounds/checkmate.wav"),
        'promotion': pygame.mixer.Sound("assets/sounds/promotion.wav"),
        'game_over': pygame.mixer.Sound("assets/sounds/game_over.wav")
    }
    return sounds

# Play sound based on event type
def play_sound(event_type, sounds):
    if event_type in sounds:
        sounds[event_type].play()

