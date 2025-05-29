import os
import json
import torch
import random
import numpy as np
from collections import deque

from main import Main
from ai_controller import get_valid_actions, get_lowest_valid_y, extract_features, evaluate_board
from models.dqn_model import DQN
from replay_memory import ReplayMemory
from train_utils import train_step
from settings import COLUMNS, ROWS, TETROMINOS

# === Config ===
EPISODES = 500
MAX_STEPS = 1000
EPSILON_START = 0.8
EPSILON_END = 0.1
EPSILON_DECAY = 0.995
BATCH_SIZE = 64
GAMMA = 0.99
LEARNING_RATE = 0.0005
MEMORY_SIZE = 10000
TARGET_UPDATE_FREQ = 10

SAVE_PATH = "models"
PRETRAINED_MODEL = os.path.join(SAVE_PATH, "dqn_pretrained.pt")
GA_WEIGHTS_PATH = "saved_weights/best_weights_1748039070.json"
os.makedirs(SAVE_PATH, exist_ok=True)

def train_agent():
    main = Main()
    model = DQN()
    target_model = DQN()

    if os.path.exists(PRETRAINED_MODEL):
        print("\n🔁 Loading pretrained model...")
        model.load_state_dict(torch.load(PRETRAINED_MODEL))
        target_model.load_state_dict(model.state_dict())
        model.eval()
    else:
        target_model.load_state_dict(model.state_dict())

    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    memory = ReplayMemory(MEMORY_SIZE)
    epsilon = EPSILON_START

    with open(GA_WEIGHTS_PATH, "r") as f:
        ga_weights = json.load(f)

    for episode in range(EPISODES):
        main.reset_game()
        state = extract_features([[1 if cell else 0 for cell in row] for row in main.ai_game.field_data])
        total_reward = 0
        steps = 0

        while not main.ai_game.game_over and steps < MAX_STEPS:
            piece_type = main.ai_game.tetromino.shape
            board = [[1 if cell else 0 for cell in row] for row in main.ai_game.field_data]
            valid_actions = get_valid_actions(piece_type, board)

            if not valid_actions:
                break

            # === Exploration strategy with GA fallback ===
            if random.random() < epsilon:
                # Instead of random move, use GA heuristic
                best_score = float('-inf')
                best_action = None
                for rot_idx, x_pos in valid_actions:
                    rotation = TETROMINOS[piece_type]['rotations'][rot_idx]
                    y = get_lowest_valid_y(rotation, x_pos, board)
                    if y is None:
                        continue
                    temp_board = [row[:] for row in board]
                    for dx, dy in rotation:
                        px, py = x_pos + dx, y + dy
                        if 0 <= px < COLUMNS and 0 <= py < ROWS:
                            temp_board[py][px] = 1
                    score = evaluate_board(temp_board, ga_weights)
                    if score > best_score:
                        best_score = score
                        best_action = (rot_idx, x_pos)
                action = best_action or random.choice(valid_actions)
            else:
                q_values = []
                actions = []
                for (rot_idx, x_pos) in valid_actions:
                    rotation = TETROMINOS[piece_type]['rotations'][rot_idx]
                    y = get_lowest_valid_y(rotation, x_pos, board)
                    if y is None:
                        continue
                    temp_board = [row[:] for row in board]
                    for dx, dy in rotation:
                        px, py = x_pos + dx, y + dy
                        if 0 <= px < COLUMNS and 0 <= py < ROWS:
                            temp_board[py][px] = 1
                    features = extract_features(temp_board)
                    with torch.no_grad():
                        q = model(features.unsqueeze(0)).item()
                    q_values.append(q)
                    actions.append((rot_idx, x_pos))
                action = actions[np.argmax(q_values)] if actions else random.choice(valid_actions)

            prev_lines = main.ai_score.lines
            rot_idx, x_pos = action
            main.ai_game.apply_action(piece_type, rot_idx, x_pos)
            lines_cleared = main.ai_score.lines - prev_lines
            next_state = extract_features([[1 if cell else 0 for cell in row] for row in main.ai_game.field_data])
            max_height = max([ROWS - y for y in range(ROWS) if any(board[y])]) if any(any(row) for row in board) else 0
            reward = lines_cleared * 10 - 0.2 * max_height

            memory.push(state, action, reward, next_state, main.ai_game.game_over)
            state = next_state
            total_reward += reward
            steps += 1

            if len(memory) > BATCH_SIZE:
                loss = train_step(model, target_model, memory, optimizer, batch_size=BATCH_SIZE, gamma=GAMMA)

        if episode % TARGET_UPDATE_FREQ == 0:
            target_model.load_state_dict(model.state_dict())

        if epsilon > EPSILON_END:
            epsilon *= EPSILON_DECAY

        print(f"Episode {episode+1}/{EPISODES} | Steps: {steps} | Reward: {total_reward:.1f} | Epsilon: {epsilon:.3f}")

        if (episode + 1) % 50 == 0:
            torch.save(model.state_dict(), os.path.join(SAVE_PATH, f"dqn_ep{episode+1}.pt"))
            print(f"Model saved at episode {episode+1}")

if __name__ == "__main__":
    train_agent()
