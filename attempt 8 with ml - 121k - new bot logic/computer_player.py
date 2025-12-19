import chess
import random
import time
import torch
import numpy as np
from torch import nn

# -------------------------------
# PyTorch Model Definition
# -------------------------------
class ChessEvaluator(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(12, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.fc_layers = nn.Sequential(
            nn.Linear(128*8*8 + 5, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
    
    def forward(self, board, extra):
        x = self.conv_layers(board)
        x = x.view(x.size(0), -1)
        x = torch.cat([x, extra], dim=1)
        return self.fc_layers(x)

# Global model instance
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ChessEvaluator().to(device)
model.load_state_dict(torch.load("chess_evaluator.pth"))
model.eval()

# Cache for neural network evaluations
nn_cache = {}
MAX_CACHE_SIZE = 10000

# -------------------------------
# Board to Tensor Conversion
# -------------------------------
def board_to_tensor(board):
    """Convert chess board to PyTorch tensor"""
    tensor = torch.zeros((12, 8, 8), dtype=torch.float32)
    piece_to_channel = {
        chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2,
        chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5
    }
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            channel = piece_to_channel[piece.piece_type]
            if piece.color == chess.BLACK:
                channel += 6
            row, col = 7 - square // 8, square % 8
            tensor[channel, row, col] = 1
    
    extra = torch.tensor([
        board.has_kingside_castling_rights(chess.WHITE),
        board.has_queenside_castling_rights(chess.WHITE),
        board.has_kingside_castling_rights(chess.BLACK),
        board.has_queenside_castling_rights(chess.BLACK),
        board.turn == chess.WHITE
    ], dtype=torch.float32)
    
    return tensor.unsqueeze(0), extra.unsqueeze(0)

# -------------------------------
# Neural Network Evaluation with Caching
# -------------------------------
def nn_evaluate(board):
    """Evaluate position using neural network with caching"""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    
    fen = board.fen()
    if fen in nn_cache:
        return nn_cache[fen]
    
    board_tensor, extra_features = board_to_tensor(board)
    with torch.no_grad():
        evaluation = model(
            board_tensor.to(device),
            extra_features.to(device)
        ).item() * 1000  # Scale to centipawns
    
    # Add aggression bonus based on material imbalance
    material_diff = sum(
        PIECE_VALUES[pt] * (len(board.pieces(pt, chess.WHITE)) - len(board.pieces(pt, chess.BLACK)))
        for pt in PIECE_VALUES
    )
    aggression_bonus = 0
    if abs(material_diff) > 200:  # Significant material advantage
        # Encourage aggressive play when ahead
        aggression_bonus = material_diff * 0.1
    
    evaluation += aggression_bonus
    
    # Manage cache size
    if len(nn_cache) >= MAX_CACHE_SIZE:
        nn_cache.clear()
    
    nn_cache[fen] = evaluation
    return evaluation

# -------------------------------
# Phase Detection and Bonuses
# -------------------------------
def game_phase(board):
    """Detect current game phase for aggressive play"""
    # Count pieces
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    minors = len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK)) + \
             len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK))
    
    # Determine phase
    if queens == 0 or (queens == 2 and minors <= 4):
        return "endgame"
    elif board.fullmove_number < 10:
        return "opening"
    return "middlegame"

def attack_bonus(board):
    """Bonus for attacking moves in middlegame"""
    bonus = 0
    phase = game_phase(board)
    
    if phase == "middlegame":
        # Bonus for pieces in enemy territory
        for color in [chess.WHITE, chess.BLACK]:
            enemy_side = 4 if color == chess.WHITE else 3
            for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                for square in board.pieces(piece_type, color):
                    rank = chess.square_rank(square)
                    if (color == chess.WHITE and rank >= enemy_side) or \
                       (color == chess.BLACK and rank <= enemy_side):
                        bonus += 15 if color == chess.WHITE else -15
        
        # Bonus for checks
        for move in board.legal_moves:
            if board.gives_check(move):
                bonus += 10 if board.turn == chess.WHITE else -10
    
    return bonus

# -------------------------------
# Opening Book
# -------------------------------
# Expand opening book for strategic diversity
OPENING_BOOK = {
    # Existing openings
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": [
        "e2e4", "d2d4", "c2c4", "g1f3", "b1c3"  # Added Nc3
    ],
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR": [
        "d7d5", "e7e5", "g8f6", "c7c6", "e7e6"   # Added c6 and e6
    ],
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": [
        "d7d5", "g8f6", "e7e6", "c7c5", "f7f5"   # Added c5 and f5
    ],
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": [
        "c7c5", "e7e5", "c7c6", "e7e6", "g8f6"   # Added e6 and Nf6
    ],
    
    # New strategic openings
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": [
        "f1c4", "f1b5", "d2d4"  # Italian Game options
    ],
    "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": [
        "f1c4", "b1c3", "d2d4"  # Bishop development
    ],
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R": [
        "g8f6", "f8c5", "a7a6"  # Respond to Italian
    ]
}

def get_opening_move(board):
    """Safe opening move selection with legal move check"""
    fen = board.fen().split(" ")[0]
    if fen in OPENING_BOOK:
        legal_moves = []
        for uci in OPENING_BOOK[fen]:
            try:
                move = chess.Move.from_uci(uci)
                if move in board.legal_moves:
                    legal_moves.append(move)
            except:
                continue
        if legal_moves:
            return random.choice(legal_moves)
    return None

# Piece values for aggressive play
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Transposition table for search results
transposition_table = {}
MAX_TT_SIZE = 10000

# -------------------------------
# Aggressive Search Algorithms
# -------------------------------
def order_moves(board):
    """MVV/LVA move ordering for aggressive play"""
    def score(move):
        # Prioritize captures
        if board.is_capture(move):
            victim = board.piece_type_at(move.to_square) or 0
            attacker = board.piece_type_at(move.from_square) or 0
            return 10 * PIECE_VALUES.get(victim, 0) - PIECE_VALUES.get(attacker, 0)
        
        # Prioritize checks
        if board.gives_check(move):
            return 500
        
        # Prioritize promotions
        if move.promotion:
            return 300
            
        # Default value
        return 0
        
    moves = list(board.legal_moves)
    moves.sort(key=score, reverse=True)
    return moves

def quiesce(board, alpha, beta):
    """Quiescence search to capture aggressive tactics"""
    stand_pat = nn_evaluate(board) + attack_bonus(board)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
        
    # Consider captures and checks
    for move in board.legal_moves:
        if not (board.is_capture(move) or board.gives_check(move)):
            continue
            
        board.push(move)
        score = -quiesce(board, -beta, -alpha)
        board.pop()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            
    return alpha

def alphabeta(board, depth, alpha, beta, maximizing):
    """Alpha-beta search with transposition table"""
    # Check transposition table
    key = board.fen()
    if key in transposition_table:
        tt_entry = transposition_table[key]
        if tt_entry["depth"] >= depth:
            if tt_entry["flag"] == "exact":
                return tt_entry["score"], tt_entry["best_move"]
            elif tt_entry["flag"] == "lowerbound":
                alpha = max(alpha, tt_entry["score"])
            elif tt_entry["flag"] == "upperbound":
                beta = min(beta, tt_entry["score"])
                
            if alpha >= beta:
                return tt_entry["score"], tt_entry["best_move"]

    # Terminal node or depth limit
    if depth == 0 or board.is_game_over():
        qs = quiesce(board, alpha, beta)
        return qs, None

    best_move = None
    best_score = -99999 if maximizing else 99999
    flag = "upperbound" if maximizing else "lowerbound"

    for move in order_moves(board):
        board.push(move)
        score, _ = alphabeta(board, depth - 1, -beta, -alpha, not maximizing)
        score = -score
        board.pop()
        
        if maximizing:
            if score > best_score:
                best_score = score
                best_move = move
                if best_score > alpha:
                    alpha = best_score
                    flag = "exact"
                if alpha >= beta:
                    flag = "lowerbound"
                    break
        else:
            if score < best_score:
                best_score = score
                best_move = move
                if best_score < beta:
                    beta = best_score
                    flag = "exact"
                if beta <= alpha:
                    flag = "upperbound"
                    break

    # Store in transposition table
    if len(transposition_table) >= MAX_TT_SIZE:
        transposition_table.clear()
        
    transposition_table[key] = {
        "score": best_score,
        "best_move": best_move,
        "depth": depth,
        "flag": flag
    }
    
    return best_score, best_move

# -------------------------------
# Move Selection with Resource Control
# -------------------------------
def select_best_move(board, difficulty):
    """Balanced move selection with aggression control"""
    # Use opening book for first few moves
    if board.fullmove_number < 6:
        move = get_opening_move(board)
        if move:
            return move
    
    # Difficulty settings - more aggressive at higher levels
    time_limits = {"easy": 1.5, "medium": 3.0, "hard": 5.0}
    depth_settings = {"easy": 2, "medium": 3, "hard": 4}
    
    start_time = time.time()
    best_move = None
    depth = 1
    
    # Clear transposition table periodically
    global transposition_table
    if len(transposition_table) > MAX_TT_SIZE * 0.9:
        transposition_table.clear()
    
    # Use GPU warm-up
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    
    # Iterative deepening
    while depth <= depth_settings[difficulty]:
        maximizing = board.turn == chess.WHITE
        score, current_move = alphabeta(board, depth, -99999, 99999, maximizing)
        
        if current_move:
            best_move = current_move
        
        # Check time limit
        elapsed = time.time() - start_time
        if elapsed > time_limits[difficulty]:
            break
            
        depth += 1
    
    # Fallback to aggressive move if none found
    if best_move is None:
        legal_moves = order_moves(board)
        if legal_moves:
            return legal_moves[0]  # Most aggressive move
    
    return best_move