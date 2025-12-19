draw2.py
import pygame
import chess
import time
from config import BOARD_SIZE, SQUARE_SIZE, SIDEBAR_WIDTH, LEFTBAR_WIDTH, TOPBAR_HEIGHT, BOTTOMBAR_HEIGHT, WIDTH, HEIGHT

# Extended UI Constants
MINI_PANEL_WIDTH = SQUARE_SIZE * 3  # For displaying mini boards
EXTENDED_WIDTH = MINI_PANEL_WIDTH + LEFTBAR_WIDTH + BOARD_SIZE + SIDEBAR_WIDTH

# Initialize display surface
pygame.init()
win = pygame.display.set_mode((EXTENDED_WIDTH, HEIGHT))

# Draw the main chessboard
def draw_game_board():
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            rect = pygame.Rect(
                MINI_PANEL_WIDTH + LEFTBAR_WIDTH + col * SQUARE_SIZE,
                TOPBAR_HEIGHT + row * SQUARE_SIZE,
                SQUARE_SIZE,
                SQUARE_SIZE
            )
            pygame.draw.rect(win, color, rect)

# Draw sidebars (timer and move history)
def draw_sidebars(move_log, white_time, black_time):
    # Mini Panel (for mini boards)
    pygame.draw.rect(win, (230, 230, 230), (0, 0, MINI_PANEL_WIDTH, HEIGHT))

    # Left sidebar - Timer
    pygame.draw.rect(win, (235, 235, 250), (MINI_PANEL_WIDTH, 0, LEFTBAR_WIDTH, HEIGHT))
    timer_font = pygame.font.SysFont("Consolas", 20)
    win.blit(timer_font.render("Black", True, (0, 0, 0)), (MINI_PANEL_WIDTH + 5, 10))
    win.blit(timer_font.render(time.strftime('%M:%S', time.gmtime(black_time)), True, (0, 0, 0)), (MINI_PANEL_WIDTH + 5, 30))
    win.blit(timer_font.render("White", True, (0, 0, 0)), (MINI_PANEL_WIDTH + 5, HEIGHT - BOTTOMBAR_HEIGHT - 50))
    win.blit(timer_font.render(time.strftime('%M:%S', time.gmtime(white_time)), True, (0, 0, 0)), (MINI_PANEL_WIDTH + 5, HEIGHT - BOTTOMBAR_HEIGHT - 30))

    # Right sidebar - Move History
    history_x = MINI_PANEL_WIDTH + LEFTBAR_WIDTH + BOARD_SIZE
    pygame.draw.rect(win, (255, 253, 208), (history_x, 0, SIDEBAR_WIDTH, HEIGHT))
    font = pygame.font.SysFont("Arial", 18)
    win.blit(font.render("Moves", True, (0, 0, 0)), (history_x + 10, 10))
    for i in range(0, len(move_log), 2):
        move_text = f"{i//2+1}. {move_log[i]}"
        if i+1 < len(move_log):
            move_text += f" {move_log[i+1]}"
        win.blit(font.render(move_text, True, (0, 0, 0)), (history_x + 10, 40 + (i//2)*20))

# Draw two large mini-boards in the far-left panel showing pre and AI-thinks state
def draw_sidebar_gameboards(pre_board, ai_move, candidate_moves=None):
    from chess_pieces import images
    panel_x = 0
    y0 = TOPBAR_HEIGHT + 20
    mini = SQUARE_SIZE * 3
    square = mini // 8

    def draw_mini(board, moves_marker=None, chosen_move=None, offset_y=0):
        pygame.draw.rect(win, (240,240,240), (panel_x, y0+offset_y, mini, mini))
        for r in range(8):
            for c in range(8):
                color = (240,217,181) if (r+c)%2==0 else (181,136,99)
                px = panel_x + c*square
                py = y0 + offset_y + r*square
                pygame.draw.rect(win, color, (px, py, square, square))
                sq = chess.square(c, 7-r)
                piece = board.piece_at(sq)
                if piece:
                    key = ('w' if piece.color==chess.WHITE else 'b') + piece.symbol().upper()
                    if key in images:
                        img = pygame.transform.smoothscale(images[key], (square, square))
                        win.blit(img, (px, py))

        # Highlight candidate moves
        if moves_marker:
            for m in moves_marker:
                to = m.to_square
                c = chess.square_file(to)
                r = 7 - chess.square_rank(to)
                px = panel_x + c*square + square//2
                py = y0 + offset_y + r*square + square//2
                pygame.draw.circle(win, (0,0,255), (px, py), 5)

        # Highlight chosen move
        if chosen_move:
            from_sq, to_sq = chosen_move.from_square, chosen_move.to_square
            fx, fy = chess.square_file(from_sq), 7 - chess.square_rank(from_sq)
            tx, ty = chess.square_file(to_sq), 7 - chess.square_rank(to_sq)
            start = (panel_x + fx*square + square//2, y0 + offset_y + fy*square + square//2)
            end = (panel_x + tx*square + square//2, y0 + offset_y + ty*square + square//2)
            pygame.draw.line(win, (255,0,0), start, end, 3)

    # Draw the two mini boards
    draw_mini(pre_board, offset_y=0)
    win.blit(pygame.font.SysFont("arial",14).render("Before",True,(0,0,0)), (panel_x, y0-18))

    draw_mini(pre_board, candidate_moves, ai_move, offset_y=mini+30)
    win.blit(pygame.font.SysFont("arial",14).render("AI Thinks",True,(0,0,0)), (panel_x, y0+mini+10))

# Draw the top bar of buttons
def draw_topbar():
    import sound
    button_font = pygame.font.SysFont("Arial",22)
    area = pygame.Rect(MINI_PANEL_WIDTH+LEFTBAR_WIDTH, 0, BOARD_SIZE, TOPBAR_HEIGHT)
    pygame.draw.rect(win, (200,200,200), area)
    button_w, button_h, gap = 100, 35, 15
    start_x = MINI_PANEL_WIDTH+LEFTBAR_WIDTH + (BOARD_SIZE - (3*button_w+2*gap))//2
    y = (TOPBAR_HEIGHT-button_h)//2
    btns = {}
    for txt in ["Mute","Restart","End"]:
        rect = pygame.Rect(start_x, y, button_w, button_h)
        pygame.draw.rect(win, (100,100,100), rect)
        pygame.draw.rect(win, (0,0,0), rect,2)
        win.blit(button_font.render(txt,True,(255,255,255)), rect.center)
        btns[txt]=rect
        start_x+=button_w+gap
    return btns

# Draw bottom message bar
def draw_bottombar(message):
    rect = pygame.Rect(MINI_PANEL_WIDTH+LEFTBAR_WIDTH, HEIGHT-BOTTOMBAR_HEIGHT, BOARD_SIZE, BOTTOMBAR_HEIGHT)
    pygame.draw.rect(win,(220,220,220),rect)
    txt = pygame.font.SysFont("Arial",20).render(message,True,(0,0,0))
    win.blit(txt,(rect.x+10, rect.y+10))

# Draw rank/file labels
def draw_labels():
    font=pygame.font.SysFont("Arial",16)
    for i in range(8):
        rtxt=font.render(str(8-i),True,(0,0,0))
        win.blit(rtxt,(MINI_PANEL_WIDTH+LEFTBAR_WIDTH-20, TOPBAR_HEIGHT+i*SQUARE_SIZE+SQUARE_SIZE//2-8))
        ftxt=font.render(chr(ord('a')+i),True,(0,0,0))
        win.blit(ftxt,(MINI_PANEL_WIDTH+LEFTBAR_WIDTH+i*SQUARE_SIZE+SQUARE_SIZE//2-8, TOPBAR_HEIGHT+8*SQUARE_SIZE+5))
