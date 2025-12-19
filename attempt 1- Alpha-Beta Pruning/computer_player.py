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

def alphabeta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    for move in board.legal_moves:
        board.push(move)
        score, _ = alphabeta(board, depth - 1, alpha, beta, not maximizing)
        board.pop()

        if maximizing:
            if score > alpha:
                alpha, best_move = score, move
            if alpha >= beta:
                break  # Beta cutoff
        else:
            if score < beta:
                beta, best_move = score, move
            if beta <= alpha:
                break  # Alpha cutoff

    return (alpha, best_move) if maximizing else (beta, best_move)

def select_best_move(board, depth=2):
    maximizing = board.turn == chess.WHITE
    _, best_move = alphabeta(board, depth, float('-inf'), float('inf'), maximizing)
    return best_move

