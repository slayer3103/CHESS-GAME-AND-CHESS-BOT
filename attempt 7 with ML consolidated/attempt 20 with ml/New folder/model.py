import torch.nn as nn
import torch

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
            nn.Linear(128*8*8 + 5, 256),  # +5 for extra features
            nn.ReLU(),
            nn.Linear(256, 1)
        )
    
    def forward(self, board, extra):
        x = self.conv_layers(board)
        x = x.view(x.size(0), -1)  # Flatten
        x = torch.cat([x, extra], dim=1)
        return self.fc_layers(x)