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

def evaluate_board(board):
    """
    Simple material evaluation: positive for White, negative for Black.
    """
    value = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            sign = 1 if piece.color == chess.WHITE else -1
            value += sign * PIECE_VALUES.get(piece.piece_type, 0)
    return value

def order_moves(board):
    """
    Return legal moves sorted so that captures come first, using MVV/LVA.
    """
    def mvv_lva_score(move):
        victim_type = board.piece_type_at(move.to_square)
        attacker_type = board.piece_type_at(move.from_square)
        # Higher score for capturing a high-value victim with a low-value attacker
        return (10 * PIECE_VALUES.get(victim_type, 0)
                - PIECE_VALUES.get(attacker_type, 0))
    moves = list(board.legal_moves)
    # Sort descending: captures (high score) first
    moves.sort(key=mvv_lva_score, reverse=True)
    return moves

def alphabeta(board, depth, alpha, beta, maximizing):
    """
    Alpha-beta pruning search with move ordering.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    for move in order_moves(board):
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
    """
    Entry point: returns best_move found by alpha-beta, or a random fallback.
    """
    maximizing = (board.turn == chess.WHITE)
    score, best_move = alphabeta(board, depth, float('-inf'), float('inf'), maximizing)
    if best_move is None:
        # No legal moves or search failed: fallback to random
        legal = list(board.legal_moves)
        return random.choice(legal) if legal else None
    return best_move
