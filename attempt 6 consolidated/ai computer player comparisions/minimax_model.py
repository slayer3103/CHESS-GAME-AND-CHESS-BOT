import chess
import random

# Simple piece value evaluation
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # King is not assigned a score as it's not capturable
}



def evaluate_board(board):
    """
    Evaluate the board based on material count.
    Positive for white, negative for black.
    """
    value = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            multiplier = 1 if piece.color == chess.WHITE else -1
            value += multiplier * PIECE_VALUES.get(piece.piece_type, 0)
    return value

def minimax(board, depth, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    legal_moves = list(board.legal_moves)

    if is_maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return min_eval, best_move

def select_best_move(board, depth=2):
    _, best_move = minimax(board, depth, is_maximizing=(board.turn == chess.WHITE))
    return best_move
