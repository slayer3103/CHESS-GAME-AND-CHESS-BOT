import chess.pgn
import random

def extract_sample_simple(input_path, output_path, sample_size=3000):
    """Simpler version that doesn't need game counting"""
    with open(input_path) as f, open(output_path, 'w') as out:
        games = []
        while True:
            offset = f.tell()
            headers = chess.pgn.read_headers(f)
            if headers is None:
                break
            games.append(offset)
        
        selected = random.sample(games, min(sample_size, len(games)))
        
        for offset in selected:
            f.seek(offset)
            game = chess.pgn.read_game(f)
            print(game, file=out, end='\n\n')

extract_sample_simple("lichess_games.pgn", "sample_3000.pgn")