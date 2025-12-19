import pygame 
import sys
import chess 
import time
from config import BOARD_SIZE, SQUARE_SIZE, RIGHTBAR_WIDTH, LEFTBAR_WIDTH, TOPBAR_HEIGHT, BOTTOMBAR_HEIGHT,MINI_PANEL_WIDTH, WIDTH, HEIGHT


pygame.init()


win = pygame.display.set_mode((WIDTH, HEIGHT))

def draw_sidebar_gameboards(pre_board, ai_move, candidate_moves=None):
    pygame.draw.rect(win, (255,255,255), (0, 0, MINI_PANEL_WIDTH, HEIGHT))

    from chess_pieces import images

    # Panel layout
    mini_size = MINI_PANEL_WIDTH
    panel_x = 0
    y0 = TOPBAR_HEIGHT + SQUARE_SIZE // 4
    gap = int(1.5 * SQUARE_SIZE)

    square = mini_size // 8  # scale 8×8 into mini_size

    def draw_mini_full(board, moves_marker=None, chosen_move=None, offset_y=0):
        # Draw the 8×8 mini‑board background
        pygame.draw.rect(win, (240,240,240),
                         (panel_x, y0 + offset_y, mini_size, mini_size))
        colors = [(240,217,181), (181,136,99)]
        for r in range(8):
            for c in range(8):
                px = panel_x + c * square
                py = y0 + offset_y + r * square
                color = colors[(r + c) % 2]
                pygame.draw.rect(win, color, (px, py, square, square))

                # Draw piece if present
                sq = chess.square(c, 7 - r)
                piece = board.piece_at(sq)
                if piece:
                    key = ('W' if piece.color == chess.WHITE else 'B') \
                          + piece.symbol().upper()
                    img = images[key]
                    img_s = pygame.transform.smoothscale(img, (square, square))
                    win.blit(img_s, (px, py))

        # Highlight candidate moves (optional blue dots)
        if moves_marker:
            for mv in moves_marker:
                tx = chess.square_file(mv.to_square)
                tr = 7 - chess.square_rank(mv.to_square)
                cx = panel_x + tx * square + square // 2
                cy = y0 + offset_y + tr * square + square // 2
                pygame.draw.circle(win, (0,0,255), (cx, cy), 4)

        # Draw arrow for chosen_move
        if chosen_move:
            fx, fr = chess.square_file(chosen_move.from_square), \
                     7 - chess.square_rank(chosen_move.from_square)
            tx, tr = chess.square_file(chosen_move.to_square), \
                     7 - chess.square_rank(chosen_move.to_square)
            start = (panel_x + fx * square + square//2,
                     y0 + offset_y + fr * square + square//2)
            end   = (panel_x + tx * square + square//2,
                     y0 + offset_y + tr * square + square//2)
            pygame.draw.line(win, (255,0,0), start, end, 2)


    # Before move snapshot
    draw_mini_full(pre_board, None, None, offset_y=0)
    win.blit(pygame.font.SysFont("Arial",14).render("Before", True, (0,0,0)),
             (panel_x, y0 - 18))

    # AI thinks snapshot
    draw_mini_full(pre_board, candidate_moves, ai_move,
                   offset_y=mini_size + gap)
    win.blit(pygame.font.SysFont("Arial",14).render("AI Thinks", True, (0,0,0)),
             (panel_x, y0 + mini_size + gap - 18))


def draw_time_sidebar(white_time, black_time):
    panel_x = MINI_PANEL_WIDTH
    pygame.draw.rect(win, (235,235,250), (panel_x,0, LEFTBAR_WIDTH, HEIGHT))
    tf = pygame.font.SysFont("Consolas", 20)
    win.blit(tf.render("Black", True,(0,0,0)), (panel_x+5, 10))
    win.blit(tf.render(time.strftime('%M:%S',time.gmtime(black_time)),True,(0,0,0)),
             (panel_x+5, 30))
    win.blit(tf.render("White", True,(0,0,0)),
             (panel_x+5, HEIGHT-BOTTOMBAR_HEIGHT-50))
    win.blit(tf.render(time.strftime('%M:%S',time.gmtime(white_time)),True,(0,0,0)),
             (panel_x+5, HEIGHT-BOTTOMBAR_HEIGHT-30))


def draw_game_board():
    board_x = MINI_PANEL_WIDTH + LEFTBAR_WIDTH
    colors  = [pygame.Color(240,217,181), pygame.Color(181,136,99)]
    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(
                board_x + c*SQUARE_SIZE,
                TOPBAR_HEIGHT + r*SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE
            )
            pygame.draw.rect(win, colors[(r+c)%2], rect)

def draw_move_log(move_log):
    panel_x = MINI_PANEL_WIDTH + LEFTBAR_WIDTH + BOARD_SIZE
    pygame.draw.rect(win, (255,253,208),
                     (panel_x,0, RIGHTBAR_WIDTH, HEIGHT))
    f = pygame.font.SysFont("Arial",18)
    win.blit(f.render("Moves",True,(0,0,0)), (panel_x+10,10))
    for i in range(0,len(move_log),2):
        txt = f"{i//2+1}. {move_log[i]}"
        if i+1 < len(move_log):
            txt += f" {move_log[i+1]}"
        win.blit(f.render(txt,True,(0,0,0)),
                 (panel_x+10, 40+(i//2)*20))

def draw_topbar(win):
    import sound
    font = pygame.font.SysFont("Arial", 22)
    area = pygame.Rect(LEFTBAR_WIDTH + MINI_PANEL_WIDTH, 0,
                       BOARD_SIZE, TOPBAR_HEIGHT)
    pygame.draw.rect(win, (200,200,200), area)

    btn_w, btn_h, gap = 100, 35, 15
    x = LEFTBAR_WIDTH + MINI_PANEL_WIDTH + (BOARD_SIZE - (3*btn_w + 2*gap))//2
    y = (TOPBAR_HEIGHT - btn_h)//2

    buttons = {}
    for txt in ["Mute", "Restart", "End"]:
        r = pygame.Rect(x, y, btn_w, btn_h)
        pygame.draw.rect(win, (100,100,100), r)
        pygame.draw.rect(win, (0,0,0), r, 2)

        # Fix: Center the text correctly
        text_surf = font.render(txt, True, (255,255,255))
        text_rect = text_surf.get_rect(center=r.center)
        win.blit(text_surf, text_rect)

        buttons[txt] = r
        x += btn_w + gap

    return buttons


def draw_bottombar(win, message):
    r = pygame.Rect(
        LEFTBAR_WIDTH + MINI_PANEL_WIDTH,
        HEIGHT - BOTTOMBAR_HEIGHT,
        BOARD_SIZE,
        BOTTOMBAR_HEIGHT
    )
    pygame.draw.rect(win, (220,220,220), r)
    msg = pygame.font.SysFont("Arial",20).render(message, True, (0,0,0))
    win.blit(msg, (r.x+10, r.y+10))

def draw_labels(win):
    font = pygame.font.SysFont("Arial",16)
    for i in range(8):
        # rank
        rt = font.render(str(8-i), True, (0,0,0))
        win.blit(rt, (
            LEFTBAR_WIDTH + MINI_PANEL_WIDTH - 20,
            TOPBAR_HEIGHT + i*SQUARE_SIZE + SQUARE_SIZE//2 - 8
        ))
        # file
        ft = font.render(chr(ord('a')+i), True, (0,0,0))
        win.blit(ft, (
            LEFTBAR_WIDTH + MINI_PANEL_WIDTH + i*SQUARE_SIZE + SQUARE_SIZE//2 - 8,
            TOPBAR_HEIGHT + 8*SQUARE_SIZE + 5
        ))
