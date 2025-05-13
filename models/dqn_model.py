import torch
import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, state_size=207, action_size=40):
        super().__init__()

        self.model = nn.Sequential(
            nn.Linear(state_size, 128), # input layer
            nn.ReLU(),
            nn.Linear(128,64), # hidden 
            nn.ReLU(),
            nn.Linear(64, action_size) # output layer
        )

    def forward(self, state):
        return self.model(state)