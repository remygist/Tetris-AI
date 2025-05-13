import torch
from models.dqn_model import DQN

state_size = 207
action_size = 40

# create a network to train and one to evaluate
policy_net = DQN(state_size, action_size)
target_net = DQN(state_size, action_size)

# copy weights from policy to target
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()  # use as evaluation reference

state = torch.rand((1, state_size))  
q_values = policy_net(state)

print("Q-values shape:", q_values.shape)