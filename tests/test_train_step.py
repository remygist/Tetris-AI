import torch
import torch.optim as optim
from models.dqn_model import DQN
from replay_memory import ReplayMemory
from train_utils import train_step

state_size = 207
action_size = 40
batch_size = 32

policy_net = DQN(state_size, action_size)
target_net = DQN(state_size, action_size)
target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.Adam(policy_net.parameters(), lr=0.001)
memory = ReplayMemory(1000)

# fill memory with fake transitions
for _ in range(100):
    state = torch.rand(state_size)
    action = torch.randint(0, action_size, (1,)).item()
    reward = torch.rand(1).item()
    next_state = torch.rand(state_size)
    done = torch.rand(1).item() > 0.9  # ~10% chance the game ended

    memory.push(state, action, reward, next_state, done)

# run one training step
print("Training once with a batch...")
loss = train_step(policy_net, target_net, memory, optimizer, batch_size=batch_size)

print("Done.")
print(loss)

