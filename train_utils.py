import torch
import torch.nn.functional as F

def train_step(policy_net, target_net, replay_memory, optimizer, batch_size=32, gamma=0.99):
    if len(replay_memory) < batch_size:
        return None

    # sample transitions
    batch = replay_memory.sample(batch_size)
    state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

    # convert to tensors
    state_batch = torch.stack(state_batch)
    action_batch = torch.tensor(action_batch).unsqueeze(1)  # shape [batch_size, 1]
    reward_batch = torch.tensor(reward_batch, dtype=torch.float32)
    next_state_batch = torch.stack(next_state_batch)
    done_batch = torch.tensor(done_batch, dtype=torch.float32)

    # get predicted q-values
    q_values = policy_net(state_batch).gather(1, action_batch).squeeze()

    # get predicted q-values for next state
    with torch.no_grad():
        next_q_values = target_net(next_state_batch)
        max_next_q_values = next_q_values.max(1)[0]

    # calc the target q-values
    target_q_values = reward_batch + gamma * max_next_q_values * (1 - done_batch)

    # calc the loss
    loss = F.mse_loss(q_values, target_q_values)

    # backpropagation
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item()
