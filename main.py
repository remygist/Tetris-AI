from settings import *
from sys import exit
import torch
import random

# components
from game.game import Game
from interface.score import Score
from interface.preview import Preview
from interface.start_screen import draw_start_screen, draw_difficulty_screen
from interface.game_over_screen import draw_game_over_screen
from game.bag_generator import BagGenerator
from ai_controller import get_lowest_valid_y, get_valid_actions, extract_features
from ga.ga import run_ga

class Main:
    def __init__(self):
        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Tetris')
        self.input_blocked_until = 0
        self.menu_buttons = []

        # ai delay
        self.ai_move_delay = 1000
        self.last_ai_move_time = 0
        self.player_lost_time = None
        self.min_ai_delay = 50  # milliseconds

        # random bags
        self.player_bag = BagGenerator()
        self.ai_bag = BagGenerator()

        # shapes queues
        self.player_next_shapes = [self.player_bag.get_next() for _ in range(3)]
        self.ai_next_shapes = [self.ai_bag.get_next() for _ in range(3)]

        # difficulty
        self.difficulty = None
        self.agent = None

        # components (left player, right AI)
        self.player_game = Game(self.get_player_next_shape, self.update_player_score)
        self.ai_game = Game(self.get_ai_next_shape, self.update_ai_score)

        self.player_preview = Preview(self.player_next_shapes, topleft=(PADDING, PADDING))
        self.ai_preview = Preview(self.ai_next_shapes, topleft=(WINDOW_WIDTH // 2 + PADDING, PADDING))

        self.state = 'main_menu'

    def update_player_score(self, lines, score, level):
        self.player_score.lines = lines
        self.player_score.score = score
        self.player_score.level = level

    def update_ai_score(self, lines, score, level):
        self.ai_score.lines = lines
        self.ai_score.score = score
        self.ai_score.level = level

    def get_player_next_shape(self):
        next_shape = self.player_next_shapes.pop(0)
        self.player_next_shapes.append(self.player_bag.get_next())
        return next_shape

    def get_ai_next_shape(self):
        next_shape = self.ai_next_shapes.pop(0)
        self.ai_next_shapes.append(self.ai_bag.get_next())
        return next_shape

    def reset_game(self):
        self.player_lost_time = None
        self.player_bag = BagGenerator()
        self.player_next_shapes = [self.player_bag.get_next() for _ in range(3)]

        self.ai_bag = BagGenerator()
        self.ai_next_shapes = [self.ai_bag.get_next() for _ in range(3)]

        player_gamefield_pos = (PADDING + SIDEBAR_WIDTH + PADDING, PADDING)
        player_sidebar_pos = (PADDING, PADDING)

        ai_gamefield_pos = (player_gamefield_pos[0] + GAME_WIDTH + PADDING * 2, PADDING)
        ai_sidebar_pos = (ai_gamefield_pos[0] + GAME_WIDTH + PADDING, PADDING)

        self.player_game = Game(self.get_player_next_shape, self.update_player_score, topleft=player_gamefield_pos)
        self.ai_game = Game(self.get_ai_next_shape, self.update_ai_score, topleft=ai_gamefield_pos)

        self.player_game.accept_input = True
        self.ai_game.accept_input = False

        self.player_preview = Preview(self.player_next_shapes, topleft=player_sidebar_pos)
        self.ai_preview = Preview(self.ai_next_shapes, topleft=ai_sidebar_pos)

        self.player_score = Score(topleft=(PADDING, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION + PADDING * 2))
        self.ai_score = Score(topleft=(ai_sidebar_pos[0], GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION + PADDING * 2))

    def run(self):
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # buttons per screen
            if self.state == 'main_menu':
                for event in events:
                    for button in self.menu_buttons:
                        button.handle_event(event)

            elif self.state == 'difficulty_select':
                if pygame.time.get_ticks() > self.input_blocked_until:
                    for event in events:
                        for button in self.difficulty_buttons:
                            button.handle_event(event)

            elif self.state == 'game_over':
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        self.reset_game()
                        self.state = 'playing'
                        self.input_blocked_until = pygame.time.get_ticks() + 200

            # draw main and selection screen
            self.display_surface.fill(GRAY)

            if self.state == 'main_menu':
                self.menu_buttons = draw_start_screen(self, self.display_surface)

            elif self.state == 'difficulty_select':
                self.difficulty_buttons = draw_difficulty_screen(self, self.display_surface)

            elif self.state == 'playing':
                # avoid instant placing after game start
                if pygame.time.get_ticks() < self.input_blocked_until:
                    self.player_game.run([])
                else:
                    self.player_game.run(events)

                self.ai_game.run([])

                # ai 
                current_time = pygame.time.get_ticks()
                if not self.ai_game.game_over and current_time - self.last_ai_move_time > self.ai_move_delay:
                    piece_type = self.ai_game.tetromino.shape
                    board = [[1 if cell else 0 for cell in row] for row in self.ai_game.field_data]
                    valid_actions = get_valid_actions(piece_type, board)

                    best_q = float('-inf')
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
                        features = extract_features(temp_board)
                        with torch.no_grad():
                            q = self.agent(features.unsqueeze(0)).item()
                        if q > best_q:
                            best_q = q
                            best_action = (rot_idx, x_pos)
                    action = best_action

                    # difficulty tweaking
                    if self.difficulty == 'easy' and self.ai_game.current_level > 5:
                        chance = self.ai_game.current_level / 15
                        if random.random() < chance and valid_actions:
                            action = random.choice(valid_actions)

                    elif self.difficulty == 'medium' and self.ai_game.current_level > 15:
                        chance = self.ai_game.current_level / 100
                        if random.random() < chance and valid_actions:
                            action = random.choice(valid_actions)

                    if action:
                        rot_idx, x_pos = action
                        self.ai_game.apply_action(piece_type, rot_idx, x_pos)
                        self.last_ai_move_time = current_time

                # draw UI 
                self.player_score.run()
                self.ai_score.run()
                self.player_preview.run()
                self.ai_preview.run()

                # overlay if one player loses
                overlay = pygame.Surface((WINDOW_WIDTH // 2, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                font = pygame.font.SysFont(None, 36)

                if self.player_game.game_over and not self.ai_game.game_over:
                    
                    if self.player_lost_time is None:
                        self.player_lost_time = pygame.time.get_ticks()

                    # reduce ai delay over time 
                    elapsed = pygame.time.get_ticks() - self.player_lost_time
                    speedup = min(elapsed / 10000, 1)  
                    self.ai_move_delay = int(500 - speedup * 450)
                    self.ai_move_delay = max(self.ai_move_delay, self.min_ai_delay)

                    self.display_surface.blit(overlay, (0, 0))
                    line1 = font.render("You lost.", True, "white")
                    line2 = font.render("Waiting for AI...", True, "white")

                    line1_rect = line1.get_rect(center=(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2))
                    line2_rect = line2.get_rect(center=(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2 + 30))

                    self.display_surface.blit(line1, line1_rect)
                    self.display_surface.blit(line2, line2_rect)


                elif self.ai_game.game_over and not self.player_game.game_over:
                    self.display_surface.blit(overlay, (WINDOW_WIDTH // 2, 0))
                    line1 = font.render("AI lost.", True, "white")
                    line2 = font.render("You can still play!", True, "white")
                    
                    line1_rect = line1.get_rect(center=(3 * WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2))
                    line2_rect = line2.get_rect(center=(3 * WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2 + 30))

                    self.display_surface.blit(line1, line1_rect)
                    self.display_surface.blit(line2, line2_rect)

                # game ends
                if self.player_game.game_over and self.ai_game.game_over:
                    self.state = 'game_over'

            elif self.state == 'game_over':
                self.game_over_buttons = draw_game_over_screen(self, self.display_surface)
                for event in events:
                    for button in self.game_over_buttons:
                        button.handle_event(event)
                        
            pygame.display.update()
            self.clock.tick()




if __name__ == '__main__':
    main = Main()
    main.run()
