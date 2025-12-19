# game_screen.py

import pygame
import chess
import sys
import time as pytime
import tkinter as tk
from tkinter import filedialog

from sound import play_sound, toggle_mute, is_muted, load_sounds
from welcome_screen import draw_welcome_screen, handle_welcome_events, get_game_status
from config import (
    BOARD_SIZE, SQUARE_SIZE, SIDEBAR_WIDTH, LEFTBAR_WIDTH,
    TOPBAR_HEIGHT, BOTTOMBAR_HEIGHT, WIDTH, HEIGHT
)
from draw_board import draw_game_board, draw_bottombar, draw_sidebars, draw_topbar
from chess_pieces import load_images, draw_pieces, highlight_squares
from computer_player import select_best_move

# Load resources
sounds = load_sounds()
images = load_images()

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont("arial", 24)
pygame.display.set_caption("Chess Game")

def ask_save_move_logs(move_log):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Save move history"
    )
    if file_path:
        with open(file_path, 'w') as f:
            for i in range(0, len(move_log), 2):
                line = f"{i//2 + 1}. {move_log[i]}"
                if i+1 < len(move_log):
                    line += f" {move_log[i+1]}"
                f.write(line + "\n")

def main(selected_opponent, difficulty=None):
    board = chess.Board()
    move_log = []
    drag_info = {'piece': None, 'from_square': None}
    selected_square = None
    running = True
    clock = pygame.time.Clock()

    white_time, black_time = 300, 300
    turn_start = pytime.time()
    message = "White to move"
    game_over = False

    while running:
        clock.tick(60)

        if not game_over:
            now = pytime.time()
            if board.turn == chess.WHITE:
                white_time -= now - turn_start
            else:
                black_time -= now - turn_start
            turn_start = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "end"

            # Topbar click handling
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                buttons = draw_topbar(win)
                if buttons["Restart"].collidepoint(x, y):
                    play_sound('click', sounds)
                    return "restart"
                if buttons["End"].collidepoint(x, y):
                    ask_save_move_logs(move_log)
                    play_sound('click', sounds)
                    return "end"
                if buttons["Mute"].collidepoint(x, y):
                    toggle_mute()
                    play_sound('click', sounds)
                    continue

            # Piece selection
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col = (x - LEFTBAR_WIDTH) // SQUARE_SIZE
                row = 7 - ((y - TOPBAR_HEIGHT) // SQUARE_SIZE)
                if 0 <= col < 8 and 0 <= row < 8:
                    square = chess.square(col, row)
                    piece = board.piece_at(square)
                    if piece and piece.color == board.turn:
                        drag_info['piece'] = piece
                        drag_info['from_square'] = square
                        selected_square = square

            # Piece drop / move
            if event.type == pygame.MOUSEBUTTONUP and drag_info['piece'] and not game_over:
                x, y = event.pos
                col = (x - LEFTBAR_WIDTH) // SQUARE_SIZE
                row = 7 - ((y - TOPBAR_HEIGHT) // SQUARE_SIZE)
                to_sq = chess.square(col, row)
                move = chess.Move(drag_info['from_square'], to_sq)
                # Promotion
                if (drag_info['piece'].piece_type == chess.PAWN and
                    chess.square_rank(to_sq) in (0, 7)):
                    move = chess.Move(drag_info['from_square'], to_sq, promotion=chess.QUEEN)

                if move in board.legal_moves:
                    san = board.san(move)
                    board.push(move)
                    play_sound('capture' if board.is_capture(move) else 'move', sounds)
                    if board.is_check(): play_sound('check', sounds)
                    move_log.append(san)
                    selected_square = None

                    # Check end conditions
                    if board.is_checkmate():
                        play_sound('checkmate', sounds)
                        message = f"Checkmate! {'White' if board.turn == chess.BLACK else 'Black'} wins!"
                        game_over = True
                    elif board.is_stalemate():
                        play_sound('game_over', sounds)
                        message = "Draw by stalemate!"
                        game_over = True
                    elif board.is_insufficient_material():
                        play_sound('game_over', sounds)
                        message = "Draw by insufficient material!"
                        game_over = True
                    elif board.is_seventyfive_moves():
                        play_sound('game_over', sounds)
                        message = "Draw by 75-move rule!"
                        game_over = True
                    elif board.is_fivefold_repetition():
                        play_sound('game_over', sounds)
                        message = "Draw by fivefold repetition!"
                        game_over = True
                    else:
                        message = "White to move" if board.turn == chess.WHITE else "Black to move"

                    # Render human move
                    draw_topbar(win)
                    draw_game_board()
                    highlight_squares(board, None)
                    draw_pieces(board, drag_info)
                    draw_sidebars(move_log, white_time, black_time)
                    draw_bottombar(message)
                    pygame.display.flip()

                    pygame.time.wait(50)

                    # AI move
                    if (selected_opponent == "computer" and
                        board.turn == chess.BLACK and
                        not board.is_game_over()):
                        depth_lookup = {"easy": 1, "medium": 2, "hard": 3}
                        search_depth = depth_lookup.get(difficulty)
                        ai_move = select_best_move(board, search_depth)

                        if ai_move in board.legal_moves:
                            san = board.san(ai_move)
                            board.push(ai_move)
                            move_log.append(san)
                            play_sound('move', sounds)
                        else:
                            message = "AI error: illegal move"
                        # Check post-AI end conditions...
                        if board.is_checkmate():
                            play_sound('checkmate', sounds)
                            message = f"Checkmate! {'White' if board.turn == chess.BLACK else 'Black'} wins!"
                            game_over = True
                        elif board.is_check():
                            play_sound('check', sounds)
                        # (other draws omitted for brevity)

                        # Render AI move
                        draw_topbar(win)
                        draw_game_board()
                        highlight_squares(board, None)
                        draw_pieces(board, {'piece': None, 'from_square': None})
                        draw_sidebars(move_log, white_time, black_time)
                        draw_bottombar(message)
                        pygame.display.flip()

                # Reset drag
                drag_info = {'piece': None, 'from_square': None}

        # Final render (in case no move)
        draw_topbar(win)
        draw_game_board()
        highlight_squares(board, selected_square)
        draw_pieces(board, drag_info)
        draw_sidebars(move_log, white_time, black_time)
        draw_bottombar(message)
        pygame.display.flip()

    return "end"


if __name__ == "__main__":
    # For direct testing, start human game
    main("human", None)
