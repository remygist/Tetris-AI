from settings import *
import torch

def get_valid_actions(piece_type, board):
    valid_actions = []

    for rotation_index, rotation in enumerate(TETROMINOS[piece_type]['rotations']):
        # get min/max x offset for current rotation
        x_offsets = [x for x, y in rotation]
        min_x = min(x_offsets)
        max_x = max(x_offsets)

        # loop all valid x_positions for this rotation
        for x_pos in range(-min_x, COLUMNS - max_x):
            y = get_lowest_valid_y(rotation, x_pos, board)
            if y is not None:
                valid_actions.append((rotation_index, x_pos))

    return valid_actions

def get_lowest_valid_y(rotation, x_position, board):
    max_y_offset = max(y for cell, y in rotation)

    for y in reversed(range(ROWS - max_y_offset)):
        valid = True

        for dx, dy in rotation:
            final_x = x_position + dx
            final_y = y + dy

            # Check bounds
            if not (0 <= final_x < COLUMNS and 0 <= final_y < ROWS):
                valid = False
                break

            # Check collision
            if board[final_y][final_x] != 0:
                valid = False
                break

        if valid:
            return y 

    return None 

def evaluate_board(board, weights):
    ROWS = len(board)
    COLUMNS = len(board[0])

    holes = 0
    heights = [0 for _ in range(COLUMNS)]
    bumpiness = 0
    lines_cleared = 0

    # heights and holes
    for x in range(COLUMNS):
        block_found = False
        for y in range(ROWS):
            if board[y][x] != 0:
                if not block_found:
                    heights[x] = ROWS - y
                    block_found = True
            elif block_found:
                holes += 1

    # bumpiness
    for x in range(COLUMNS - 1):
        bumpiness += abs(heights[x] - heights[x + 1])

    # lines cleared
    for row in board:
        if all(cell != 0 for cell in row):
            lines_cleared += 1

    # max column height
    max_height = max(heights)

    # wells
    wells = 0
    for x in range(1, COLUMNS - 1):
        if heights[x] < heights[x - 1] and heights[x] < heights[x + 1]:
            wells += (heights[x - 1] - heights[x]) + (heights[x + 1] - heights[x])

    # row transitions
    row_transitions = 0
    for row in board:
        prev = 1  # wall on left
        for cell in row:
            if cell != prev:
                row_transitions += 1
            prev = cell
        if prev == 0:
            row_transitions += 1  # right wall

    # column transitions
    col_transitions = 0
    for x in range(COLUMNS):
        prev = 1  # floor
        for y in range(ROWS):
            cell = board[y][x]
            if cell != prev:
                col_transitions += 1
            prev = cell

    # final weighted score using all 8 features
    score = (
        weights[0] * holes +
        weights[1] * lines_cleared +
        weights[2] * bumpiness +
        weights[3] * sum(heights) +       # total_height
        weights[4] * max_height +
        weights[5] * wells +
        weights[6] * row_transitions +
        weights[7] * col_transitions
    )

    return score

def pick_best_action(piece_type, board, weights=None):
    if weights is None:
        # fallback to default weights
        weights = [-5.0, 3.0, -0.5, -0.1]

    best_score = float('-inf')
    best_action = None

    for rotation_index, x_pos in get_valid_actions(piece_type, board):
        rotation = TETROMINOS[piece_type]['rotations'][rotation_index]
        y = get_lowest_valid_y(rotation, x_pos, board)

        if y is None:
            continue
        
        # simulate dropping the piece
        temp_board = [row[:] for row in board]
        for dx, dy in rotation:
            px = x_pos + dx
            py = y + dy
            if 0 <= px < COLUMNS and 0 <= py < ROWS:
                temp_board[py][px] = 1

        # evaluate the resulting board
        score = evaluate_board(temp_board, weights)
        if score > best_score:
            best_score = score
            best_action = (rotation_index, x_pos)

    return best_action

def extract_features(board):
    ROWS = len(board)
    COLUMNS = len(board[0])

    holes = 0
    heights = [0 for _ in range(COLUMNS)]
    bumpiness = 0
    lines_cleared = 0

    for x in range(COLUMNS):
        block_found = False
        for y in range(ROWS):
            if board[y][x] != 0:
                if not block_found:
                    heights[x] = ROWS - y
                    block_found = True
            elif block_found:
                holes += 1

    for x in range(COLUMNS - 1):
        bumpiness += abs(heights[x] - heights[x + 1])

    max_height = max(heights)
    total_height = sum(heights)

    wells = 0
    for x in range(1, COLUMNS - 1):
        if heights[x] < heights[x - 1] and heights[x] < heights[x + 1]:
            wells += (heights[x - 1] - heights[x]) + (heights[x + 1] - heights[x])

    row_transitions = 0
    for row in board:
        prev = 1
        for cell in row:
            if cell != prev:
                row_transitions += 1
            prev = cell
        if prev == 0:
            row_transitions += 1

    col_transitions = 0
    for x in range(COLUMNS):
        prev = 1
        for y in range(ROWS):
            cell = board[y][x]
            if cell != prev:
                col_transitions += 1
            prev = cell

    return torch.tensor([
        holes,
        lines_cleared,
        bumpiness,
        total_height,
        max_height,
        wells,
        row_transitions,
        col_transitions
    ], dtype=torch.float32)

