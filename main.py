from settings import *
from sys import exit
import torch
import random
import os
import json

# components
from game.game import Game
from interface.score import Score
from interface.preview import Preview
from interface.start_screen import draw_start_screen, draw_difficulty_screen
from interface.game_over_screen import draw_game_over_screen
from interface.stats_screen import draw_stats_screen
from game.bag_generator import BagGenerator
from ai_controller import get_lowest_valid_y, get_valid_actions, extract_features
from ga.ga import run_ga

class Main:
    def __init__(self):
        # general setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('NEUROBLOCKS')
        self.input_blocked_until = 0
        self.menu_buttons = []

        # ai timing control
        self.last_ai_move_time = 0
        self.player_lost_time = None
        self.min_ai_delay = 50  # milliseconds

        # difficulty
        self.difficulty = None
        self.agent = None

        # stats
        self.load_stats()
        self.prev_player_lines = 0
        self.prev_ai_lines     = 0

        # init state
        self.state = 'main_menu'

    def init_stats(self):
        return {
            'games_played': 0,
            'games_won': 0,
            'history': [],
            'total_player_score': 0,
            'total_ai_score': 0,
            'total_player_moves': 0,
            'total_ai_moves': 0,
            'total_player_lines': 0,
            'total_ai_lines': 0,
            'total_player_holes': 0,
            'total_ai_holes': 0,
            'total_player_tetrises': 0,
            'total_ai_tetrises': 0
        }

    def update_player_score(self, lines, score, level):
        # Update display score
        self.player_score.lines = lines
        self.player_score.score = score
        self.player_score.level = level

        # track line clears and tetrises
        delta = lines - self.prev_player_lines
        if delta > 0:
            self.stats['total_player_lines'] += delta
            if delta == 4:
                self.stats['total_player_tetrises'] += 1
        self.prev_player_lines = lines

    def update_ai_score(self, lines, score, level):
        # Update display score
        self.ai_score.lines = lines
        self.ai_score.score = score
        self.ai_score.level = level

        # track line clears and tetrises
        delta = lines - self.prev_ai_lines
        if delta > 0:
            self.stats['total_ai_lines'] += delta
            if delta == 4:
                self.stats['total_ai_tetrises'] += 1
        self.prev_ai_lines = lines

    def get_player_next_shape(self):
        next_shape = self.player_next_shapes.pop(0)
        self.player_next_shapes.append(self.player_bag.get_next())
        return next_shape

    def get_ai_next_shape(self):
        next_shape = self.ai_next_shapes.pop(0)
        self.ai_next_shapes.append(self.ai_bag.get_next())
        return next_shape

    def reset_game(self):
        self.ai_move_delay = 1000

        # shapes queue
        self.player_bag = BagGenerator()
        self.player_next_shapes = [self.player_bag.get_next() for _ in range(3)]
        self.ai_bag = BagGenerator()
        self.ai_next_shapes = [self.ai_bag.get_next() for _ in range(3)]

        # position gamefields and ui
        player_gamefield_pos = (PADDING + SIDEBAR_WIDTH + PADDING, PADDING)
        player_sidebar_pos = (PADDING, PADDING)

        ai_gamefield_pos = (player_gamefield_pos[0] + GAME_WIDTH + PADDING * 2, PADDING)
        ai_sidebar_pos = (ai_gamefield_pos[0] + GAME_WIDTH + PADDING, PADDING)

        self.player_game = Game(self, self.get_player_next_shape, self.update_player_score, topleft=player_gamefield_pos)
        self.ai_game = Game(self, self.get_ai_next_shape, self.update_ai_score, topleft=ai_gamefield_pos)

        self.player_game.accept_input = True
        self.ai_game.accept_input = False

        self.player_preview = Preview(self.player_next_shapes, topleft=player_sidebar_pos)
        self.ai_preview = Preview(self.ai_next_shapes, topleft=ai_sidebar_pos)

        self.player_score = Score(topleft=(PADDING, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION + PADDING * 2))
        self.ai_score = Score(topleft=(ai_sidebar_pos[0], GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION + PADDING * 2))

        # reset stats
        keys = [
        'total_player_moves','total_ai_moves',
        'total_player_lines','total_ai_lines',
        'total_player_holes','total_ai_holes',
        'total_player_tetrises','total_ai_tetrises'
    ]
        for k in keys:
            self.stats[k] = 0
        self.prev_player_lines = 0
        self.prev_ai_lines     = 0

    def record_stats(self):
        # add games won to stats
        self.stats['games_played'] += 1
        if self.player_score.score > self.ai_score.score:
            self.stats['games_won'] += 1

        # get board features
        player_board = [[1 if cell else 0 for cell in row] for row in self.player_game.field_data]
        ai_board     = [[1 if cell else 0 for cell in row] for row in self.ai_game.field_data]

        player_feats = extract_features(player_board)
        ai_feats = extract_features(ai_board)

        player_holes = int(player_feats[0].item())
        ai_holes = int(ai_feats[0].item())

        entry = {
            'player_score': self.player_score.score,
            'ai_score': self.ai_score.score,
            'player_lines': self.stats['total_player_lines'],
            'ai_lines': self.stats['total_ai_lines'],
            'player_moves': self.stats['total_player_moves'],
            'ai_moves': self.stats['total_ai_moves'],
            'player_holes': player_holes,
            'ai_holes': ai_holes,
            'player_tetrises': self.stats['total_player_tetrises'],
            'ai_tetrises': self.stats['total_ai_tetrises'],
        }
        self.stats['history'].append(entry)

        # update totals
        self.stats['total_player_holes'] += player_holes
        self.stats['total_ai_holes'] += ai_holes
        self.stats['total_player_score'] += self.player_score.score
        self.stats['total_ai_score'] += self.ai_score.score

    def run(self):
        while True:
            events = pygame.event.get()

            # quit game
            for event in events:
                if event.type == pygame.QUIT:
                    self.save_stats()     
                    pygame.quit()
                    exit()

            # buttons main menu
            if self.state == 'main_menu':
                for event in events:
                    for button in self.menu_buttons:
                        button.handle_event(event)

           # buttons difficulty menu
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

            # draw main background
            self.display_surface.fill(GRAY)

            # draw main menu
            if self.state == 'main_menu':
                self.menu_buttons = draw_start_screen(self, self.display_surface)
            
            # draw difficulty menu
            elif self.state == 'difficulty_select':
                self.difficulty_buttons = draw_difficulty_screen(self, self.display_surface)
            

            elif self.state == 'playing':
                # avoid instant placing after game start
                if pygame.time.get_ticks() < self.input_blocked_until:
                    self.player_game.run([])
                else:
                    self.player_game.run(events)

                # run ai game logic
                self.ai_game.run([])

                # ai choose move
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

                    # apply ai move
                    if action:
                        rot_idx, x_pos = action
                        self.ai_game.apply_action(piece_type, rot_idx, x_pos)
                        self.stats['total_ai_moves'] += 1
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
                    self.record_stats()
                    self.state = 'game_over'

            # draw game over screen
            elif self.state == 'game_over':
                self.game_over_buttons = draw_game_over_screen(self, self.display_surface)
                for event in events:
                    for button in self.game_over_buttons:
                        button.handle_event(event)
            
            # draw stats screen
            elif self.state == 'stats':
                buttons = draw_stats_screen(self, self.display_surface)
                for event in pygame.event.get():
                    for btn in buttons:
                        btn.handle_event(event)
    
            pygame.display.update()
            self.clock.tick()

    def load_stats(self):
        if os.path.isfile('stats.json'):
            try:
                with open('stats.json', 'r') as f:
                    data = json.load(f)
                base = self.init_stats()
                base.update({k: data.get(k, base[k]) for k in base})
                base['history'] = data.get('history', [])
                self.stats = base
            except Exception:
                self.stats = self.init_stats()
        else:
            self.stats = self.init_stats()

    def save_stats(self):
        try:
            to_save = {
                k: self.stats[k]
                for k in self.stats
                if k != 'history' or isinstance(self.stats['history'], list)
            }
            with open('stats.json', 'w') as f:
                json.dump(to_save, f, indent=2)
        except Exception as e:
            print("Error saving stats:", e)

if __name__ == '__main__':
    main = Main()
    main.run()
