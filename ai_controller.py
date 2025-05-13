from settings import *

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

def evaluate_board(board):
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
            if board[y][x] != 0: # check if filled
                if not block_found:
                    heights[x] = ROWS - y  
                    block_found = True # highest block found
                else:
                    continue  # already counted height
            elif block_found:
                holes += 1  # space below a filled block

    # bumpiness
    for x in range(COLUMNS - 1):
        bumpiness += abs(heights[x] - heights[x + 1])

    # lines cleared
    for row in board:
        if all(cell != 0 for cell in row):
            lines_cleared += 1

    total_height = sum(heights)

    # final weighted score
    score = (
        -5.0 * holes +
         3.0 * lines_cleared +
        -0.5 * bumpiness +
        -0.1 * total_height
    )

    return score

def pick_best_action(piece_type, board):
    best_score = float('-inf') # negative infinite so every score is better
    best_action = None

    for rotation_index, x_pos in get_valid_actions(piece_type, board):
        rotation = TETROMINOS[piece_type]['rotations'][rotation_index]
        y = get_lowest_valid_y(rotation, x_pos, board)

        if y is None:
            continue

        # copy board
        temp_board = [row[:] for row in board]

        # apply pieces in temp board
        for dx, dy in rotation:
            px = x_pos + dx
            py = y + dy
            if 0 <= px < COLUMNS and 0 <= py < ROWS:
                temp_board[py][px] = 1
        
        score = evaluate_board(temp_board)
        if score > best_score:
            best_score = score
            best_action = (rotation_index, x_pos)
        
    return best_action
