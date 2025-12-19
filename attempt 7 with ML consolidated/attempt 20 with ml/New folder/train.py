from chess_dataset import ChessDataset
from model import ChessEvaluator
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from tqdm import tqdm

def main():
    # Initialize
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = ChessDataset("sample_1000.pgn")
    model = ChessEvaluator().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    # DataLoader
    dataloader = DataLoader(dataset, batch_size=128, shuffle=True)

    # Training loop
    for epoch in range(10):  # 10 epochs
        total_loss = 0
        for board, extra, _ in tqdm(dataloader):
            board = board.to(device)
            extra = extra.to(device)
            
            # Get Stockfish evaluation (placeholder - implement this)
            targets = torch.randn(len(board))  # Replace with real evaluations
            
            optimizer.zero_grad()
            outputs = model(board, extra)
            loss = criterion(outputs, targets.to(device))
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f"Epoch {epoch+1}, Loss: {total_loss/len(dataloader)}")

    # Save model
    torch.save(model.state_dict(), "chess_evaluator.pth")

if __name__ == "__main__":
    main()