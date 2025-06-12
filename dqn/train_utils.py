import torch
import torch.nn as nn
import torch.nn.functional as F

def train_step(policy_net, target_net, replay_memory, optimizer, batch_size=64, gamma=0.99):
    batch = replay_memory.sample(batch_size)

    state_batch = torch.stack([experience[0] for experience in batch])
    reward_batch = torch.tensor([experience[2] for experience in batch], dtype=torch.float32).unsqueeze(1)
    next_state_batch = torch.stack([experience[3] for experience in batch])
    done_batch = torch.tensor([experience[4] for experience in batch], dtype=torch.float32).unsqueeze(1)

    # Compute Q(s, a)
    q_values = policy_net(state_batch)

    # Compute target Q-values
    with torch.no_grad():
        target_q_values = target_net(next_state_batch)
        targets = reward_batch + gamma * target_q_values * (1 - done_batch)

    # Loss = MSE between predicted and target Q-values
    loss = nn.MSELoss()(q_values, targets)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item()

