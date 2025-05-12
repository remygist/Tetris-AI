from settings import *
from ai_controller import get_lowest_valid_y, get_valid_actions, evaluate_board, pick_best_action

# Start with an empty board
board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

# Add blocks manually to simulate a situation
for y in range(16, 20):
    board[y][1] = 1
    board[y][3] = 1

# Ask AI to choose best placement for 'O'
action = pick_best_action('O', board)
print(f"Best action for 'O': Rotation {action[0]}, X = {action[1]}")
