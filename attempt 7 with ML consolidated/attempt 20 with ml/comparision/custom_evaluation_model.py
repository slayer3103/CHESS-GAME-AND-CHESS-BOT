# computer_player.py

import chess
import random

# Piece values for evaluation
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# Transposition table: key (FEN) -> (score, best_move, depth)
transposition_table = {}

# Piece-square tables for positional evaluation
PAWN_TABLE = [
     0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
     5,   5,  10,  25,  25,  10,   5,   5,
     0,   0,   0,  20,  20,   0,   0,   0,
     5,  -5, -10,   0,   0, -10,  -5,   5,
     5,  10,  10, -20, -20,  10,  10,   5,
     0,   0,   0,   0,   0,   0,   0,   0
]

KNIGHT_TABLE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
]

def evaluate_board(board):
    """Material + positional evaluation."""
    total = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            sign = 1 if piece.color == chess.WHITE else -1
            total += sign * PIECE_VALUES[piece.piece_type]
            idx = sq if piece.color == chess.WHITE else chess.square_mirror(sq)
            if piece.piece_type == chess.PAWN:
                total += sign * PAWN_TABLE[idx]
            elif piece.piece_type == chess.KNIGHT:
                total += sign * KNIGHT_TABLE[idx]
    # Center control bonus
    for center in [chess.D4, chess.D5, chess.E4, chess.E5]:
        p = board.piece_at(center)
        if p and p.piece_type == chess.PAWN:
            total += 30 if p.color == chess.WHITE else -30
    # Double pawn penalty
    for file in range(8):
        pawns = [sq for sq in chess.SQUARES
                 if chess.square_file(sq)==file
                 and board.piece_at(sq)
                 and board.piece_at(sq).piece_type==chess.PAWN]
        if len(pawns) > 1:
            color = board.piece_at(pawns[0]).color
            total -= (20 if color==chess.WHITE else -20)
    # King safety (simple open-file penalty)
    for col, ranks in [(chess.square_file(board.king(chess.WHITE)), [0,1]),
                       (chess.square_file(board.king(chess.BLACK)), [6,7])]:
        if not any(board.piece_at(chess.square(col,r)) for r in ranks):
            total += -50 if ranks==[0,1] else 50
    return total

def order_moves(board):
    """MVV/LVA move ordering: captures first."""
    def score(m):
        vic = board.piece_type_at(m.to_square) or 0
        atk = board.piece_type_at(m.from_square) or 0
        return 10 * PIECE_VALUES.get(vic,0) - PIECE_VALUES.get(atk,0)
    moves = list(board.legal_moves)
    moves.sort(key=score, reverse=True)
    return moves

def quiesce(board, alpha, beta):
    """Quiescence search: only captures."""
    stand = evaluate_board(board)
    if stand >= beta:
        return beta
    alpha = max(alpha, stand)
    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiesce(board, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            alpha = max(alpha, score)
    return alpha

def alphabeta(board, depth, alpha, beta, maximizing):
    """Alpha-beta with transposition table and quiescence."""
    key = board.fen()
    if key in transposition_table:
        s, mv, d = transposition_table[key]
        if d >= depth:
            return s, mv
    if depth == 0:
        qs = quiesce(board, alpha, beta)
        transposition_table[key] = (qs, None, depth)
        return qs, None
    if board.is_game_over():
        val = evaluate_board(board)
        transposition_table[key] = (val, None, depth)
        return val, None

    best_move = None
    moves = order_moves(board)
    for m in moves:
        board.push(m)
        score, _ = alphabeta(board, depth-1, alpha, beta, not maximizing)
        board.pop()
        if maximizing:
            if score > alpha:
                alpha, best_move = score, m
            if alpha >= beta:
                break
        else:
            if score < beta:
                beta, best_move = score, m
            if beta <= alpha:
                break

    res = (alpha, best_move) if maximizing else (beta, best_move)
    transposition_table[key] = (res[0], best_move, depth)
    return res

def select_best_move(board, depth=2):
    maximizing = (board.turn == chess.WHITE)
    score, move = alphabeta(board, depth, float('-inf'), float('inf'), maximizing)
    if not move:
        legal = list(board.legal_moves)
        return random.choice(legal) if legal else None
    return move
