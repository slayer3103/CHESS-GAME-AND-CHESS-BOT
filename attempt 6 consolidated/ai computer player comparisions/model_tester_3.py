import chess
import importlib
import time

def play_game(ai_white, ai_black, depth_white, depth_black, max_moves=200):
    board = chess.Board()
    for _ in range(max_moves):
        if board.is_game_over():
            break
        # Choose which AI to move
        if board.turn == chess.WHITE:
            move = ai_white.select_best_move(board, depth_white)
        else:
            move = ai_black.select_best_move(board, depth_black)
        if move not in board.legal_moves:
            # Illegal or None — resign
            return "0-1" if board.turn == chess.WHITE else "1-0"
        board.push(move)
    return board.result()  # "1-0", "0-1", "1/2-1/2"

def evaluate_models(ai1_name, ai2_name, depth1=2, depth2=2, games=20):
    ai1 = importlib.import_module(ai1_name)
    ai2 = importlib.import_module(ai2_name)
    results = {"ai1":0, "ai2":0, "draws":0}

    for i in range(games):
        # Alternate colors
        if i % 2 == 0:
            result = play_game(ai1, ai2, depth1, depth2)
            white = "ai1"
        else:
            result = play_game(ai2, ai1, depth2, depth1)
            white = "ai2"
        # Tally
        if result == "1-0":
            results[white] += 1
        elif result == "0-1":
            loser = "ai2" if white=="ai1" else "ai1"
            results[loser] += 1
        else:
            results["draws"] += 1
        print(f"Game {i+1}: Result {result}")

    print(f"\nFinal after {games} games:")
    print(f"  {ai1_name} wins: {results['ai1']}")
    print(f"  {ai2_name} wins: {results['ai2']}")
    print(f"  Draws      : {results['draws']}")

if __name__ == "__main__":
    # Example: compare minimax vs alpha-beta
    evaluate_models("heuristic_model", "transposition_model", depth1=2, depth2=2, games=100)
