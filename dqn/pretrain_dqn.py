import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
import random

from ai_controller import evaluate_board, extract_features
from models.dqn_model import DQN
from settings import COLUMNS, ROWS

# config
SAMPLES = 5000
BATCH_SIZE = 64
EPOCHS = 5
LEARNING_RATE = 0.001
GA_WEIGHTS_PATH = "saved_weights/best_weights_1748039070.json"
SAVE_PATH = "models/dqn_pretrained.pt"

def generate_random_board():
    board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
    # fill with random blocks
    for y in range(ROWS):
        for x in range(COLUMNS):
            if random.random() < 0.1:  # 10% chance of being filled
                board[y][x] = 1
    return board

def main():
    with open(GA_WEIGHTS_PATH, "r") as f:
        ga_weights = json.load(f)

    data = []
    for _ in range(SAMPLES):
        board = generate_random_board()
        features = extract_features(board)
        score = evaluate_board(board, ga_weights)
        data.append((features, score))

    model = DQN()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    loss_fn = nn.MSELoss()

    for epoch in range(EPOCHS):
        random.shuffle(data)
        total_loss = 0
        for i in range(0, len(data), BATCH_SIZE):
            batch = data[i:i+BATCH_SIZE]
            x_batch = torch.stack([item[0] for item in batch])
            y_batch = torch.tensor([item[1] for item in batch], dtype=torch.float32).unsqueeze(1)

            preds = model(x_batch)
            loss = loss_fn(preds, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / (len(data) / BATCH_SIZE)
        print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {avg_loss:.4f}")

    torch.save(model.state_dict(), SAVE_PATH)
    print(f"\n✅ Pretrained DQN model saved to: {SAVE_PATH}")

if __name__ == "__main__":
    main()
