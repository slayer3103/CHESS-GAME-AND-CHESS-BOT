import pygame
import chess
import time as pytime
import threading
import tkinter as tk
from tkinter import filedialog

from sound import play_sound, toggle_mute, is_muted, load_sounds
from welcome_screen import get_game_status
from config import (
    BOARD_SIZE, SQUARE_SIZE, RIGHTBAR_WIDTH, LEFTBAR_WIDTH,
    TOPBAR_HEIGHT, BOTTOMBAR_HEIGHT, MINI_PANEL_WIDTH, WIDTH, HEIGHT
)
from draw_board import draw_game_board, draw_bottombar, draw_time_sidebar, draw_move_log, draw_topbar, draw_sidebar_gameboards
from chess_pieces import load_images, draw_pieces, highlight_squares
from computer_player import select_best_move

# Load resources
sounds = load_sounds()
images = load_images()


moves_surf_height = max(HEIGHT, 2000)                # e.g. 2000 px tall
moves_surf = pygame.Surface((RIGHTBAR_WIDTH, moves_surf_height))
moves_scroll = 0                                     # initial scroll offset


pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

def ask_save_move_logs(move_log):
    root = tk.Tk(); root.withdraw()
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

    clock = pygame.time.Clock()
    white_time, black_time = 300.0, 300.0
    message = "White to move"
    game_over = False

    ai_thread = None
    ai_move = None
    ai_thinking = False
    ai_start_time = 0.0
    pre_board = board.copy()

    while True:
        dt = clock.tick(60) / 1000.0
        if not game_over:
            if board.turn == chess.WHITE:
                white_time -= dt
            else:
                black_time -= dt

        if ai_thinking and ai_thread and not ai_thread.is_alive():
            ai_thinking = False
            elapsed = pytime.time() - ai_start_time
            black_time -= elapsed

            if ai_move and ai_move in board.legal_moves:
                san = board.san(ai_move)
                board.push(ai_move)
                play_sound('move', sounds)
                move_log.append(san)
            else:
                message = " error: illegal move"

            if board.is_checkmate():
                play_sound('checkmate', sounds)
                winner = "White" if board.turn == chess.BLACK else "Black"
                message = f"Checkmate! {winner} wins!"
                game_over = True
            elif board.is_check():
                play_sound('check', sounds)
            ai_thread = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "end"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                buttons = draw_topbar(win)

                if buttons["Restart"].collidepoint(x,y):
                    play_sound('click', sounds); return "restart"
                
                if buttons["End"].collidepoint(x,y):
                    ask_save_move_logs(move_log)
                    play_sound('click', sounds)
                    return "end"
                
                if buttons["Mute"].collidepoint(x,y):
                    toggle_mute(); play_sound('click', sounds)
                    continue
            
            if event.type == pygame.MOUSEWHEEL:
                moves_scroll = max(0, min(moves_scroll - event.y * 20, moves_surf_height - HEIGHT))

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x,y = event.pos
                col = (x - LEFTBAR_WIDTH - MINI_PANEL_WIDTH)//SQUARE_SIZE
                row = 7 - ((y - TOPBAR_HEIGHT)//SQUARE_SIZE)

                if 0<=col<8 and 0<=row<8:
                    sq = chess.square(col,row)
                    piece = board.piece_at(sq)
                    if piece and piece.color==board.turn:
                        drag_info['piece'] = piece
                        drag_info['from_square'] = sq
                        selected_square = sq

            if (event.type == pygame.MOUSEBUTTONUP and drag_info['piece'] and not game_over):
                x,y = event.pos
                col = (x - LEFTBAR_WIDTH - MINI_PANEL_WIDTH)//SQUARE_SIZE
                row = 7 - ((y - TOPBAR_HEIGHT)//SQUARE_SIZE)
                to_sq = chess.square(col,row)
                move = chess.Move(drag_info['from_square'], to_sq)

                if (drag_info['piece'].piece_type==chess.PAWN and chess.square_rank(to_sq) in (0,7)):
                    move = chess.Move(drag_info['from_square'], to_sq, promotion=chess.QUEEN)

                if move in board.legal_moves:
                    san = board.san(move)
                    board.push(move)
                    play_sound('capture' if board.is_capture(move) else 'move', sounds)

                    if board.is_check():
                        play_sound('check', sounds)
                    move_log.append(san)
                    selected_square = None

                    if board.is_checkmate():
                        play_sound('checkmate', sounds)
                        winner = "White" if board.turn==chess.BLACK else "Black"
                        message = f"Checkmate! {winner} wins!"
                        game_over = True

                    elif board.is_stalemate():
                        play_sound('game_over', sounds); message = "Draw by stalemate!"; game_over = True

                    elif board.is_insufficient_material():
                        play_sound('game_over', sounds); message = "Draw by insufficient material!"; game_over=True

                    elif board.is_seventyfive_moves():
                        play_sound('game_over', sounds); message = "Draw by 75-move rule!"; game_over=True

                    elif board.is_fivefold_repetition():
                        play_sound('game_over', sounds); message = "Draw by fivefold repetition!"; game_over=True

                    else:
                        message = "White to move" if board.turn==chess.WHITE else "Black to move"

                    if (selected_opponent=="computer" and board.turn==chess.BLACK and not board.is_game_over() and not ai_thinking):
                        pre_board = board.copy()
                        ai_move = None
                        ai_thinking = True
                        ai_start_time = pytime.time()

                        def ai_worker():
                            nonlocal ai_move
                            ai_move = select_best_move(board.copy(), difficulty)
                        ai_thread = threading.Thread(target=ai_worker, daemon=True)
                        ai_thread.start()

                drag_info = {'piece':None, 'from_square':None}

       
        draw_sidebar_gameboards(pre_board, ai_move)
        draw_time_sidebar(white_time, black_time)
        draw_move_log(move_log)
        draw_topbar(win)
        draw_game_board()
        highlight_squares(board, selected_square)
        draw_pieces(board, drag_info)
        draw_bottombar(win, message)
        pygame.display.flip()