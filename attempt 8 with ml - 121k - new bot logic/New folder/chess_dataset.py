import chess
import chess.pgn
import torch
from torch.utils.data import Dataset
import random

class ChessDataset(Dataset):
    def __init__(self, pgn_path, max_games=3000):
        self.positions = self._process_pgn(pgn_path, max_games)
    
    def _process_pgn(self, pgn_path, max_games):
        positions = []
        with open(pgn_path) as f:
            game_count = 0
            while game_count < max_games:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                board = game.board()
                for move in game.mainline_moves():
                    board.push(move)
                    if random.random() < 0.2:  # Sample 20% of positions
                        positions.append(self._board_to_features(board))
                game_count += 1
        return positions
    
    def _board_to_features(self, board):
        # Convert board to tensor
        tensor = torch.zeros((12, 8, 8))  # 12 channels for piece types
        
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
        
        # Additional features
        extra = torch.tensor([
            board.has_kingside_castling_rights(chess.WHITE),
            board.has_queenside_castling_rights(chess.WHITE),
            board.has_kingside_castling_rights(chess.BLACK),
            board.has_queenside_castling_rights(chess.BLACK),
            board.turn == chess.WHITE
        ], dtype=torch.float32)
        
        return tensor, extra, torch.tensor([0.0])  # Dummy target (will replace)

    def __len__(self):
        return len(self.positions)

    def __getitem__(self, idx):
        return self.positions[idx]