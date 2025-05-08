from settings import *
from ai_controller import get_lowest_valid_y, get_valid_actions

# Step 1: Create an empty board
board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

# Step 2: Optionally simulate a filled block
for y in range(ROWS):  # rows 16 to 19 (bottom)
    board[y][1] = 1  # left pillar
    board[y][4] = 1  # right pillar

# Step 3: Call get_valid_actions
piece_type = 'T'
actions = get_valid_actions(piece_type, board)

print(f"\nValid actions for '{piece_type}':")
for rot_idx, x in actions:
    print(f" - Rotation {rot_idx}, X = {x}")