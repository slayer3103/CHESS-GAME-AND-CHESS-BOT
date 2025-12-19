import pygame
import chess
from draw_board import draw_game_board, draw_bottombar, draw_sidebars, draw_topbar
from config import BOARD_SIZE, SQUARE_SIZE, SIDEBAR_WIDTH, LEFTBAR_WIDTH, TOPBAR_HEIGHT, BOTTOMBAR_HEIGHT, WIDTH, HEIGHT


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

win = pygame.display.set_mode((WIDTH, HEIGHT))

# Draw pieces
def draw_pieces(board, drag_info=None):
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
