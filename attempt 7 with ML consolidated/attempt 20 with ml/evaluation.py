import chess
import time
from computer_player import select_best_move  # Import your bot

# Test positions with known best moves
TEST_POSITIONS = [
    {
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
        "best_moves": ["d2d4"],  # Multiple good moves possible
        "name": "Italian Opening"
    },
    {
        "fen": "8/8/8/5k2/8/8/4K3/8 b - - 0 1",
        "best_moves": ["f5e5", "f5g5", "f5e4"],
        "name": "Knight Endgame"
    }
]

# Benchmarking function
def evaluate_model(model_name, difficulty="hard", runs=5):
    print(f"\nEvaluating {model_name} ({difficulty})...")
    results = {
        "accuracy": 0,
        "avg_time": 0,
        "positions_tested": 0
    }
    
    for position in TEST_POSITIONS:
        board = chess.Board(position["fen"])
        correct = 0
        total_time = 0
        
        for _ in range(runs):
            start_time = time.time()
            move = select_best_move(board, difficulty)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if move.uci() in position["best_moves"]:
                correct += 1
        
        accuracy = correct / runs
        avg_time = total_time / runs
        
        print(f"Position: {position['name']}")
        print(f"  Accuracy: {accuracy:.2f} | Avg Time: {avg_time:.2f}s")
        
        results["accuracy"] += accuracy
        results["avg_time"] += avg_time
        results["positions_tested"] += 1
    
    results["accuracy"] /= results["positions_tested"]
    results["avg_time"] /= results["positions_tested"]
    
    print("\nSummary:")
    print(f"Overall Accuracy: {results['accuracy']:.2f}")
    print(f"Average Move Time: {results['avg_time']:.2f}s")
    return results

if __name__ == "__main__":
    evaluate_model("YourModelName", difficulty="hard", runs=5)