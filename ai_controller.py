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
