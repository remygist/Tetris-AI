import pygame 

# game size 
COLUMNS = 10
ROWS = 20
CELL_SIZE = 40
GAME_WIDTH, GAME_HEIGHT = COLUMNS * CELL_SIZE, ROWS * CELL_SIZE

# side bar size 
SIDEBAR_WIDTH = 200
PREVIEW_HEIGHT_FRACTION = 0.7
SCORE_HEIGHT_FRACTION = 1 - PREVIEW_HEIGHT_FRACTION

# window
PADDING = 20
WINDOW_WIDTH = (SIDEBAR_WIDTH + GAME_WIDTH) * 2 + PADDING * 6  # 2 games + 2 sidebars + gaps
WINDOW_HEIGHT = GAME_HEIGHT + PADDING * 2

# game behaviour 
UPDATE_START_SPEED = 800
MOVE_WAIT_TIME = 150
ROTATE_WAIT_TIME = 100
BLOCK_OFFSET = pygame.Vector2(COLUMNS // 2, -1)
LOCK_DELAY = 200

# colors 
YELLOW = '#f1e60d'
RED = '#e51b20'
BLUE = '#204b9b'
GREEN = '#65b32e'
PURPLE = '#7b217f'
CYAN = '#6cc6d9'
ORANGE = '#f07e13'
GRAY = '#1C1C1C'
LINE_COLOR = '#FFFFFF'

# shapes
TETROMINOS = {
	'T': {
        'shape': [(0,0), (-1,0), (1,0), (0,-1)],
        'rotations': [
            [(0, 0), (-1, 0), (1, 0), (0, -1)],
			[(0, 0), (0, 1), (0, -1), (-1, 0)],
			[(0, 0), (1, 0), (-1, 0), (0, 1)],
			[(0, 0), (0, -1), (0, 1), (1, 0)]
        ],  
        'color': PURPLE},
	'O': {
        'shape': [(0,0), (0,-1), (1,0), (1,-1)],
        'rotations': [
            [(0,0), (0,-1), (1,0), (1,-1)],
			[(0,0), (0,-1), (1,0), (1,-1)],
			[(0,0), (0,-1), (1,0), (1,-1)],
			[(0,0), (0,-1), (1,0), (1,-1)]
        ],   
        'color': YELLOW},
	'J': {
        'shape': [(0,0), (0,-1), (0,1), (-1,1)],
        'rotations': [
            [(0, 0), (0, -1), (0, 1), (-1, 1)],
			[(0, 0), (-1, 0), (1, 0), (1, 1)],
			[(0, 0), (0, 1), (0, -1), (1, -1)],
			[(0, 0), (1, 0), (-1, 0), (-1, -1)]
        ],  
        'color': BLUE},
	'L': {
        'shape': [(0,0), (0,-1), (0,1), (1,1)], 
		'rotations': [
            [(0, 0), (0, -1), (0, 1), (1, 1)],
			[(0, 0), (-1, 0), (1, 0), (1, -1)],
			[(0, 0), (0, 1), (0, -1), (-1, -1)],
			[(0, 0), (1, 0), (-1, 0), (-1, 1)]
        ], 
        'color': ORANGE},
	'I': {
        'shape': [(0,0), (0,-1), (0,-2), (0,1)],
        'rotations': [
            [(0, 0), (0, -1), (0, -2), (0, 1)],
			[(0, 0), (-1, 0), (-2, 0), (1, 0)],
			[(0, 0), (0, 1), (0, 2), (0, -1)],
			[(0, 0), (1, 0), (2, 0), (-1, 0)]
        ],  
        'color': CYAN},
	'S': {
        'shape': [(0,0), (-1,0), (0,-1), (1,-1)],
        'rotations': [
            [(0, 0), (-1, 0), (0, -1), (1, -1)],
			[(0, 0), (0, 1), (-1, 0), (-1, -1)],
			[(0, 0), (1, 0), (0, 1), (-1, 1)],
			[(0, 0), (0, -1), (1, 0), (1, 1)]
        ],   
        'color': GREEN},
	'Z': {
        'shape': [(0,0), (1,0), (0,-1), (-1,-1)],
        'rotations': [
            [(0, 0), (1, 0), (0, -1), (-1, -1)],
			[(0, 0), (0, -1), (-1, 0), (-1, 1)],
			[(0, 0), (-1, 0), (0, 1), (1, 1)],
			[(0, 0), (0, 1), (1, 0), (1, -1)]
        ],    
        'color': RED}
}

SCORE_DATA = {1: 40, 2: 100, 3: 300, 4: 1200}