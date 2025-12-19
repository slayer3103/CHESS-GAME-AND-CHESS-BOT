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
# Neural Network Evaluation
# -------------------------------
def nn_evaluate(board):
    """Evaluate position using neural network"""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    
    board_tensor, extra_features = board_to_tensor(board)
    with torch.no_grad():
        evaluation = model(
            board_tensor.to(device),
            extra_features.to(device)
        ).item()
    
    return evaluation * 1000  # Scale to centipawns

# -------------------------------
# Existing Code (Keep This Section)
# -------------------------------
# Simplified opening book with legal move checking
OPENING_BOOK = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": ["e2e4", "d2d4", "c2c4", "g1f3"],
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR": ["d7d5", "e7e5", "g8f6"],
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": ["d7d5", "g8f6", "e7e6"],
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": ["c7c5", "e7e5", "c7c6"],
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

# Piece values (optimized)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# -------------------------------
# Search Algorithms (Modified)
# -------------------------------
def order_moves(board):
    """Fast move ordering - captures first, then others"""
    captures = [m for m in board.legal_moves if board.is_capture(m)]
    non_captures = [m for m in board.legal_moves if not board.is_capture(m)]
    return captures + non_captures

def alphabeta(board, depth, alpha, beta, maximizing):
    """Optimized alpha-beta with depth-based pruning"""
    # Use neural network evaluation at leaf nodes
    if depth <= 0 or board.is_game_over():
        return nn_evaluate(board), None

    best_move = None
    best_score = -99999 if maximizing else 99999
    
    for move in order_moves(board):
        board.push(move)
        score, _ = alphabeta(board, depth - 1, -beta, -alpha, not maximizing)
        score = -score  # Negate since we're alternating perspectives
        board.pop()
        
        if maximizing:
            if score > best_score:
                best_score = score
                best_move = move
                alpha = max(alpha, score)
        else:
            if score < best_score:
                best_score = score
                best_move = move
                beta = min(beta, score)
                
        if beta <= alpha:
            break
            
    return best_score, best_move

def select_best_move(board, difficulty):
    """Highly optimized move selection with strict time limits"""
    # Use opening book for first few moves
    if board.fullmove_number < 6:
        move = get_opening_move(board)
        if move:
            return move
    
    # Difficulty settings
    time_limits = {"easy": 1.5, "medium": 3.0, "hard": 5.0}
    max_depths = {"easy": 2, "medium": 3, "hard": 4}
    
    start_time = time.time()
    best_move = None
    depth = 1
    
    # Iterative deepening with strict time/depth limits
    while depth <= max_depths[difficulty]:
        maximizing = board.turn == chess.WHITE
        _, current_move = alphabeta(board, depth, -99999, 99999, maximizing)
        
        if current_move:
            best_move = current_move
        
        # Strict time control
        elapsed = time.time() - start_time
        if elapsed > time_limits[difficulty]:
            break
            
        depth += 1
    
    # Fallback to random move if needed
    if best_move is None:
        legal_moves = list(board.legal_moves)
        if legal_moves:
            return random.choice(legal_moves)
    
    return best_move