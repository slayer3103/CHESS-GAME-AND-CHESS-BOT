import pygame

pygame.mixer.init()

muted = False
loaded_sounds={}

# Load sounds
def load_sounds():
    global loaded_sounds
    loaded_sounds = {
        
        'click': pygame.mixer.Sound("assets/sounds/click.wav"),
        'move': pygame.mixer.Sound("assets/sounds/move.wav"),
        'capture': pygame.mixer.Sound("assets/sounds/capture.wav"),
        'check': pygame.mixer.Sound("assets/sounds/check.wav"),
        'checkmate': pygame.mixer.Sound("assets/sounds/checkmate.wav"),
        'promotion': pygame.mixer.Sound("assets/sounds/promotion.wav"),
        'game_over': pygame.mixer.Sound("assets/sounds/game_over.wav")
    }
    return loaded_sounds

# Play sound based on event type or if it is not muted
def play_sound(event_type, sounds):
    if not muted and event_type in sounds:
        sounds[event_type].play()

# change mute= false to  mute = true
def toggle_mute():
    global muted
    muted = not muted

# ture or false as return
def is_muted():
    return muted
    

