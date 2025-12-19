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

# Transposition table: zobrist_key → (score, best_move, depth)
transposition_table = {}

def evaluate_board(board):
    value = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            sign = 1 if piece.color == chess.WHITE else -1
            value += sign * PIECE_VALUES.get(piece.piece_type, 0)
    return value

def order_moves(board):
    def score(m):
        victim = board.piece_type_at(m.to_square) or 0
        attacker = board.piece_type_at(m.from_square) or 0
        return 10 * PIECE_VALUES.get(victim,0) - PIECE_VALUES.get(attacker,0)
    moves = list(board.legal_moves)
    moves.sort(key=score, reverse=True)
    return moves

def alphabeta(board, depth, alpha, beta, maximizing):
    # Use FEN as key if transposition_key unavailable
    key = board.fen()
    if key in transposition_table:
        stored_score, stored_move, stored_depth = transposition_table[key]
        if stored_depth >= depth:
            return stored_score, stored_move

    if depth == 0 or board.is_game_over():
        val = evaluate_board(board)
        transposition_table[key] = (val, None, depth)
        return val, None

    best_move = None
    for move in order_moves(board):
        board.push(move)
        score, _ = alphabeta(board, depth-1, alpha, beta, not maximizing)
        board.pop()

        if maximizing:
            if score > alpha:
                alpha, best_move = score, move
            if alpha >= beta:
                break
        else:
            if score < beta:
                beta, best_move = score, move
            if beta <= alpha:
                break

    result = (alpha, best_move) if maximizing else (beta, best_move)
    transposition_table[key] = (result[0], best_move, depth)
    return result

def select_best_move(board, depth=2):
    maximizing = (board.turn == chess.WHITE)
    score, best_move = alphabeta(board, depth, float('-inf'), float('inf'), maximizing)
    if best_move is None:
        legal = list(board.legal_moves)
        return random.choice(legal) if legal else None
    return best_move
