import pygame
import chess
import sys

# Constants
BOARD_SIZE = 640
SIDEBAR_WIDTH = 160
WIDTH, HEIGHT = BOARD_SIZE + SIDEBAR_WIDTH, 640
SQUARE_SIZE = BOARD_SIZE // 8

# Initialize Pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Load images
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
              'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    images = {}
    for piece in pieces:
        image = pygame.image.load(f"assets/pieces/{piece}.png")
        images[piece.upper()] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    return images

images = load_images()

# Draw the chess board
def draw_board(win):
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draw sidebar background
    sidebar_rect = pygame.Rect(BOARD_SIZE, 0, SIDEBAR_WIDTH, HEIGHT)
    pygame.draw.rect(win, (255, 253, 208), sidebar_rect)  # Light grey color

# Draw the pieces
def draw_pieces(win, board, images):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            key = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
            win.blit(images[key.upper()], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Highlight selected piece and legal moves
def highlight_squares(win, board, selected_square):
    if selected_square is not None:
        row = 7 - chess.square_rank(selected_square)
        col = chess.square_file(selected_square)
        pygame.draw.rect(win, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill((0, 255, 0, 80))  # Transparent green

        for move in board.legal_moves:
            if move.from_square == selected_square:
                to_row = 7 - chess.square_rank(move.to_square)
                to_col = chess.square_file(move.to_square)
                win.blit(highlight_surface, (to_col * SQUARE_SIZE, to_row * SQUARE_SIZE))

# Draw captured pieces
def draw_captured_pieces(win, images, captured_white, captured_black):
    x_start = BOARD_SIZE + 10
    y_offset = 10
    spacing = 40

    # Captured black pieces (top half)
    for i, piece in enumerate(captured_black):
        img = images[('B' if piece.color == chess.BLACK else 'W') + piece.symbol().upper()]
        win.blit(pygame.transform.scale(img, (30, 30)), (x_start, y_offset + i * spacing))

    # Captured white pieces (bottom half)
    for i, piece in enumerate(captured_white):
        img = images[('W' if piece.color == chess.WHITE else 'B') + piece.symbol().upper()]
        win.blit(pygame.transform.scale(img, (30, 30)), (x_start, HEIGHT // 2 + y_offset + i * spacing))

# Main game loop
def main():
    board = chess.Board()
    selected_square = None
    running = True
    captured_pieces_white = []
    captured_pieces_black = []

    while running:
        draw_board(win)
        highlight_squares(win, board, selected_square)
        draw_pieces(win, board, images)
        draw_captured_pieces(win, images, captured_pieces_white, captured_pieces_black)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if x < BOARD_SIZE:  # Inside board area
                    col = x // SQUARE_SIZE
                    row = 7 - (y // SQUARE_SIZE)
                    square = chess.square(col, row)

                    if selected_square is None:
                        if board.piece_at(square) and board.piece_at(square).color == board.turn:
                            selected_square = square
                    else:
                        move = chess.Move(selected_square, square)

                        # Handle pawn promotion
                        if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
                            move = chess.Move(selected_square, square, promotion=chess.QUEEN)

                        if move in board.legal_moves:
                            # Capture tracking
                            captured = board.piece_at(square)
                            if captured and captured.color != board.turn:
                                if board.turn == chess.WHITE:
                                    captured_pieces_black.append(captured)
                                else:
                                    captured_pieces_white.append(captured)

                            board.push(move)
                        selected_square = None

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
