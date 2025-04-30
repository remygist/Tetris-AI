from settings import *
from random import choice
from sys import exit
from timer import Timer

class Game: 
    
    def __init__(self, get_next_shape, update_score):

        # general
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft = (PADDING,PADDING))
        self.sprites = pygame.sprite.Group()
        self.game_over = False

        # game connection
        self.get_next_shape = get_next_shape
        self.update_score = update_score

        # lines
        self.line_surface = self.surface.copy()
        self.line_surface.fill((0,255,0))
        self.line_surface.set_colorkey((0,255,0))
        self.line_surface.set_alpha(120)

        # tetromino
        self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())),self.sprites,
            self.create_new_tetromino,
            self.field_data)

        # timer
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.3
        self.timers = {
            'vertical move': Timer(self.down_speed, True, self.move_down),
            'horizontal move': Timer(MOVE_WAIT_TIME),
            'move down': Timer(MOVE_WAIT_TIME),
            'rotate': Timer(ROTATE_WAIT_TIME),
            'touch down': Timer(MOVE_WAIT_TIME)
        }
        self.timers['vertical move'].activate()

        # score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0
    
    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        if self.current_lines/10 > self.current_level:
            self.current_level += 1
        self.update_score(self.current_lines, self.current_score, self.current_level)

    def check_game_over(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            if y >= 0 and self.field_data[y][x]:  # Only check visible rows
                return True
        return False

    def create_new_tetromino(self, game_over=False):
        if game_over:
            self.game_over = True
            return

        self.check_finished_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(),
            self.sprites,
            self.create_new_tetromino,
            self.field_data
    )

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        self.tetromino.move_down()

    def draw_grid(self):

        for col in range (1, COLUMNS):
            x = col * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (x,0),(x,self.surface.get_height()),1)

        for row in range (1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (0,y),(self.surface.get_width(),y),1)

        self.surface.blit(self.line_surface, (0,0))

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers['horizontal move'].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers['horizontal move'].activate()
            if keys[pygame.K_SPACE]:
                self.tetromino.touch_down()
                self.timers['horizontal move'].activate()
        
        if not self.timers['move down'].active:
            if keys[pygame.K_DOWN]:
                self.tetromino.move_down()
                self.timers['move down'].activate()

        if not self.timers['rotate'].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate()
                self.timers['rotate'].activate()

    def check_finished_rows(self):
        # get row indexes
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:
            for delete_row in delete_rows:
                # delete full rows
                for block in self.field_data[delete_row]:
                    block.kill()
                
                #move down blocks
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            # rebuild the field data
            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

            # update score
            self.calculate_score(len(delete_rows))
    def run(self):

        # update
        self.input()
        self.timer_update()
        self.sprites.update()

        # drawing
        self.surface.fill(GRAY)
        ghost_positions = self.tetromino.get_ghost_position()
        for pos in ghost_positions:
            rect = pygame.Rect(pos.x * CELL_SIZE, pos.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.surface, self.tetromino.color, rect, width=2)  # Outlined ghost

        self.sprites.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (PADDING,PADDING))
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)

class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data):

        # setup
        self.shape = shape
        self.block_positions = TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data

        # create blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    def get_ghost_position(self):
        ghost_positions = [block.pos.copy() for block in self.blocks]

        while True:
            for pos in ghost_positions:
                x, y = int(pos.x), int(pos.y + 1)
                if y >= ROWS or self.field_data[y][x]:
                    return ghost_positions  # Stop if any part would collide
            # Move all ghost blocks down
            for pos in ghost_positions:
                pos.y += 1

    # collisions
    def next_move_horizontal_collide(self, blocks, amount):
        collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False
    
    def next_move_vertical_collide(self, blocks, amount):
        collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    # movement
    def move_down(self):
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            game_over = any(block.pos.y < 0 for block in self.blocks)

            for block in self.blocks:
                y, x = int(block.pos.y), int(block.pos.x)
                if y >= 0:
                    self.field_data[y][x] = block

            self.create_new_tetromino(game_over=game_over)
    
    def move_horizontal(self, amount):
        if not self.next_move_horizontal_collide(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount
    
    def touch_down(self):
        drop_distances = []

        for block in self.blocks:
            distance = 0
            while True:
                new_y = int(block.pos.y + distance + 1)
                if new_y >= ROWS: 
                    break
                if new_y >= 0 and self.field_data[new_y][int(block.pos.x)]:
                    break
                distance += 1
            drop_distances.append(distance)

        min_drop = min(drop_distances)

        game_over = False
        for block in self.blocks:
            block.pos.y += min_drop
            if block.pos.y < 0:
                game_over = True
            y, x = int(block.pos.y), int(block.pos.x)
            if y >= 0:
                self.field_data[y][x] = block

        self.create_new_tetromino(game_over=game_over)

    # rotate
    def rotate(self):
        if self.shape != 'O':

            # pivot point
            pivot_pos = self.blocks[0].pos

            # new block pos
            new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

            # collision check
            for pos in new_block_positions:
                x, y = int(pos.x), int(pos.y)

                # Blocked by walls
                if x < 0 or x >= COLUMNS:
                    return

                # Blocked by floor
                if y >= ROWS:
                    return

                # Only check for occupied cells if within the visible field
                if y >= 0 and self.field_data[y][x]:
                    return

            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):

        # general
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE,CELL_SIZE))
        self.image.fill(color)

        # position
        self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft = self.pos * CELL_SIZE)

    def rotate(self, pivot_pos):    
        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def horizontal_collide(self,x, field_data):
        if not 0 <= x < COLUMNS:
            return True
        y = int(self.pos.y)
        if 0 <= y < ROWS and field_data[y][x]:
            return True
        return False
        
    def vertical_collide(self,y, field_data):
        if y >= ROWS:
            return True
        
        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True
        return False

    def update(self):
        self.rect.topleft = self.pos * CELL_SIZE
