import torch
import torch.nn as nn
import json
import os

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

def load_agent(agent_type, model_path=None):
    if model_path is None:
        raise ValueError("Must provide model_path for agent type: " + agent_type)
    ext = os.path.splitext(model_path)[1].lower()
    if ext == ".pt":
        model = DQN()
        model.load_state_dict(torch.load(model_path))
        model.eval()
        return model
    elif ext == ".json":
        with open(model_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file extension '{ext}'. Must be .pt or .json")
    
def set_agent_model(difficulty):
    if difficulty == "easy":
        model_path = "models/easy/dqn_easy.pt"
    elif difficulty == "medium":
        model_path = "models/dqn_medium.pt"
    elif difficulty == "hard":
        model_path = "models/dqn_hard.pt"
    else:
        raise ValueError("Invalid difficulty")

    return load_agent("dqn", model_path)


