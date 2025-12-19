import chess
import chess.pgn
import numpy as np
from sklearn.neural_network import MLPRegressor
import joblib
import io

def process_pgn_file(pgn_path):
    """Process a single PGN file containing multiple games"""
    X = []
    y = []
    
    with open(pgn_path) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
                
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                
                # Extract features
                features = []
                for square in chess.SQUARES:
                    piece = board.piece_at(square)
                    if piece:
                        val = piece.piece_type * (1 if piece.color == chess.WHITE else -1)
                    else:
                        val = 0
                    features.append(val)
                
                # Add castling rights
                features += [
                    int(board.has_kingside_castling_rights(chess.WHITE)),
                    int(board.has_queenside_castling_rights(chess.WHITE)),
                    int(board.has_kingside_castling_rights(chess.BLACK)),
                    int(board.has_queenside_castling_rights(chess.BLACK))
                ]
                
                # Get evaluation from Stockfish
                try:
                    with chess.engine.SimpleEngine.popen_uci("stockfish") as engine:
                        info = engine.analyse(board, chess.engine.Limit(time=0.1))
                        score = info["score"].white().score(mate_score=10000)
                        if score is None:  # Handle mate situations
                            score = 10000 if info["score"].white().mate() > 0 else -10000
                except:
                    # Fallback to material evaluation
                    score = sum(
                        PIECE_VALUES.get(p.piece_type, 0) * (1 if p.color == chess.WHITE else -1)
                        for p in board.piece_map().values()
                    )
                
                X.append(features)
                y.append(np.tanh(score/1000))  # Normalize to [-1, 1]
    
    return np.array(X), np.array(y)

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9
}

def train_and_save_model(pgn_path, model_path='chess_eval_model.pkl'):
    """Train and save the evaluation model"""
    X, y = process_pgn_file(pgn_path)
    
    print(f"Training on {len(X)} positions...")
    
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        max_iter=100,
        random_state=42,
        verbose=True
    )
    
    model.fit(X, y)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    return model

if __name__ == "__main__":
    train_and_save_model("sample_1000.pgn")