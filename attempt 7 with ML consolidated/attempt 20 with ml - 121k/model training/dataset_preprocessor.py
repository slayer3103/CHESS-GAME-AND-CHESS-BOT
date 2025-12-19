import chess.pgn
import random
import os

def count_games(pgn_path):
    """Count total games in PGN file"""
    with open(pgn_path) as f:
        return sum(1 for _ in chess.pgn.read_headers(f))

def extract_sample_games(pgn_path, output_path, sample_size=1000, random_seed=42):
    """
    Extract a random sample of games from a large PGN file
    Args:
        pgn_path: Path to large PGN file
        output_path: Where to save sampled games
        sample_size: Number of games to extract
        random_seed: For reproducibility
    """
    # Count total games
    total_games = count_games(pgn_path)
    print(f"Found {total_games} games in input file")
    
    # Select random game indices
    random.seed(random_seed)
    selected_indices = set(random.sample(range(total_games), min(sample_size, total_games)))
    
    # Extract selected games
    extracted = 0
    with open(pgn_path) as f, open(output_path, 'w') as out:
        while True:
            headers = chess.pgn.read_headers(f)
            if headers is None:
                break
                
            if extracted in selected_indices:
                # Get the full game
                f.seek(headers.offset)
                game = chess.pgn.read_game(f)
                print(game, file=out, end='\n\n')
                extracted += 1
                
                # Progress indicator
                if extracted % 100 == 0:
                    print(f"Extracted {extracted}/{sample_size} games")
            else:
                # Skip this game
                chess.pgn.skip_game(f)
    
    print(f"Successfully saved {extracted} games to {output_path}")

if __name__ == "__main__":
    # Example usage - adjust paths as needed
    extract_sample_games(
        pgn_path="lichess_games.pgn",
        output_path="sample_1000.pgn",
        sample_size=1000
    )