import torch
import torch.nn as nn

# deep q-network with 2 hidden layers
class DQN(nn.Module):
    def __init__(self, input_dim=8, hidden_dim1=128, hidden_dim2=64, output_dim=1):
        super(DQN, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.ReLU(),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.ReLU(),
            nn.Linear(hidden_dim2, output_dim)
        )

    def forward(self, state):
        return self.model(state)

def load_agent(model_path=None):
    model = DQN()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model
    
def set_agent_model(difficulty):
    if difficulty == "easy":
        model_path = "models/easy/dqn_easy.pt"
    elif difficulty == "medium":
        model_path = "models/medium/dqn_medium.pt"
    elif difficulty == "hard":
        model_path = "models/hard/dqn_hard.pt"

    return load_agent(model_path)


