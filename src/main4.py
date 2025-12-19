import pygame
import chess
import sys
import time
import sound  # Import the sound handling module i.e. sound.py

# Constants
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
SIDEBAR_WIDTH = 200
LEFTBAR_WIDTH = 60
TOPBAR_HEIGHT = 60
BOTTOMBAR_HEIGHT = 40

WIDTH = LEFTBAR_WIDTH + BOARD_SIZE + SIDEBAR_WIDTH
HEIGHT = TOPBAR_HEIGHT + BOARD_SIZE + BOTTOMBAR_HEIGHT

# Load sounds
sounds = sound.load_sounds()


# Initialize Pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont("arial", 24)
pygame.display.set_caption("Chess Game")

# Load piece images
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
              'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    images = {}
    for piece in pieces:
        image = pygame.image.load(f"assets/pieces/{piece}.png")
        images[piece.upper()] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    return images

images = load_images()

# Draw the board
def draw_board():
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

# Topbar (button etc)
def draw_topbar(win):
    pygame.draw.rect(win, (200, 200, 200), (0, 0, WIDTH, TOPBAR_HEIGHT))
    button_font = pygame.font.SysFont("Arial", 20)
    buttons = {
        "Restart": pygame.Rect(LEFTBAR_WIDTH + 20, 10, 100, 40),
        "End": pygame.Rect(LEFTBAR_WIDTH + 140, 10, 80, 40),
        "Mute": pygame.Rect(LEFTBAR_WIDTH + 240, 10, 80, 40)
    }
    for text, rect in buttons.items():
        pygame.draw.rect(win, (180, 180, 180), rect)
        pygame.draw.rect(win, (0, 0, 0), rect, 2)
        label = button_font.render(text, True, (0, 0, 0))
        win.blit(label, (rect.x + 10, rect.y + 10))
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

# Draw pieces
def draw_pieces(board, drag_info):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            if drag_info['piece'] and square == drag_info['from_square']:
                continue
            key = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
            win.blit(images[key.upper()], (
                LEFTBAR_WIDTH + col * SQUARE_SIZE, 
                TOPBAR_HEIGHT + row * SQUARE_SIZE
                ))

    if drag_info['piece']:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        key = ('w' if drag_info['piece'].color == chess.WHITE else 'b') + drag_info['piece'].symbol().upper()
        img = pygame.transform.scale(images[key.upper()], (SQUARE_SIZE, SQUARE_SIZE))
        win.blit(img, (mouse_x - SQUARE_SIZE // 2, mouse_y - SQUARE_SIZE // 2))

# Highlight selected square, legal moves, and checks
def highlight_squares(board, selected_square):
    if selected_square is not None:
        row = 7 - chess.square_rank(selected_square)
        col = chess.square_file(selected_square)
        pygame.draw.rect(win, (0, 255, 0), (LEFTBAR_WIDTH + col * SQUARE_SIZE, TOPBAR_HEIGHT + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill((0, 255, 0, 80))
        for move in board.legal_moves:
            if move.from_square == selected_square:
                to_row = 7 - chess.square_rank(move.to_square)
                to_col = chess.square_file(move.to_square)
                win.blit(highlight_surface, (LEFTBAR_WIDTH + to_col * SQUARE_SIZE, TOPBAR_HEIGHT + to_row * SQUARE_SIZE))

    if board.is_check():
        king_square = board.king(board.turn)
        checkers = board.checkers()
        king_row = 7 - chess.square_rank(king_square)
        king_col = chess.square_file(king_square)
        pygame.draw.rect(win, (255, 0, 0), (LEFTBAR_WIDTH + king_col * SQUARE_SIZE, TOPBAR_HEIGHT + king_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)
        for checker_square in checkers:
            row = 7 - chess.square_rank(checker_square)
            col = chess.square_file(checker_square)
            pygame.draw.rect(win, (255, 0, 0), (LEFTBAR_WIDTH + col * SQUARE_SIZE, TOPBAR_HEIGHT + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

# Main loop
def main():
    board = chess.Board()
    move_log = []
    drag_info = {'piece': None, 'from_square': None}
    running = True
    selected_square = None
    clock = pygame.time.Clock()

    white_time, black_time = 300, 300  # 5 minutes each for blitz format
    turn_start = time.time()
    message = "White to move"

    game_over = False

    while running:
        clock.tick(60)

        if not game_over: # means the game is running ?

        # Timer logic
            now = time.time()
            if board.turn == chess.WHITE:
                white_time -= now - turn_start
            else:
                black_time -= now - turn_start
            turn_start = now

        for event in pygame.event.get():
            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ...
                elif event.type == pygame.MOUSEBUTTONUP:
                    ...
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = (x - LEFTBAR_WIDTH) // SQUARE_SIZE
                row = 7 - ((y - TOPBAR_HEIGHT) // SQUARE_SIZE)
                if 0 <= col < 8 and 0 <= row < 8:
                    square = chess.square(col, row)
                    piece = board.piece_at(square)
                    if piece and piece.color == board.turn:
                        drag_info['piece'] = piece
                        drag_info['from_square'] = square
                        selected_square = square

            elif event.type == pygame.MOUSEBUTTONUP:
                if drag_info['piece']:
                    x, y = pygame.mouse.get_pos()
                    col = (x - LEFTBAR_WIDTH) // SQUARE_SIZE
                    row = 7 - ((y - TOPBAR_HEIGHT) // SQUARE_SIZE)
                    to_square = chess.square(col, row)
                    move = chess.Move(drag_info['from_square'], to_square)
                    
                    if drag_info['piece'].piece_type == chess.PAWN and chess.square_rank(to_square) in [0, 7]:
                        move = chess.Move(drag_info['from_square'], to_square, promotion=chess.QUEEN)

                        sound.play_sound('promotion', sounds)


                    if move in board.legal_moves:
                        san = board.san(move)  # ← Record SAN before making the move
                        if board.is_capture(move):
                            sound.play_sound('capture', sounds)
                        else:
                            sound.play_sound('move', sounds)

                        
                        board.push(move)
                        if board.is_check():
                            sound.play_sound('check', sounds)
                        move_log.append(san)
                        selected_square = None

                        

                        # Check for game end
                        if board.is_checkmate():
                           sound.play_sound('checkmate', sounds)
                           winner = "White" if not board.turn else "Black"
                           message = f"Checkmate! {winner} wins!"                           
                           game_over = True
                        elif board.is_stalemate():
                           sound.play_sound('game_over', sounds)
                           message = "Draw by stalemate!"
                           game_over = True
                        elif board.is_insufficient_material():
                           sound.play_sound('game_over', sounds)
                           message = "Draw by insufficient material!"                           
                           game_over = True
                        elif board.is_seventyfive_moves():
                           sound.play_sound('game_over', sounds)
                           message = "Draw by 75-move rule!"                           
                           game_over = True
                        elif board.is_fivefold_repetition():
                           sound.play_sound('game_over', sounds)
                           message = "Draw by fivefold repetition!"                           
                           game_over = True
                        else:
                           message = "White to move" if board.turn == chess.WHITE else "Black to move"

                drag_info = {'piece': None, 'from_square': None}


        # Drawing
        draw_topbar(win)
        draw_board()
        highlight_squares(board, selected_square)
        draw_labels()
        draw_pieces(board, drag_info)
        
        draw_sidebars(move_log, white_time, black_time)
        draw_bottombar(message)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
