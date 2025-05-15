from settings import *
from sys import exit

# components
from game import Game
from score import Score
from preview import Preview
from interface.start_screen import draw_start_screen
from interface.game_over_screen import draw_game_over_screen
from bag_generator import BagGenerator
from ai_controller import get_lowest_valid_y, get_valid_actions, evaluate_board, pick_best_action
from models.dqn_model import DQN
from replay_memory import ReplayMemory
from train_utils import train_step


from random import choice

class Main:
    def __init__(self):

        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Tetris')
        self.input_blocked_until = 0

        # reinforcement learning setting
        self.state_size = 207
        self.action_size = 40
        self.batch_size = 32

        self.lines_cleared_this_turn = 0

        self.policy_net = DQN(self.state_size, self.action_size)
        self.target_net = DQN(self.state_size, self.action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=0.001)
        self.replay_memory = ReplayMemory(capacity=10000)

        # ai delay
        self.ai_move_delay = 10
        self.last_ai_move_time = 0

        # random bags
        self.player_bag = BagGenerator()
        self.ai_bag = BagGenerator()

        # shapes queues
        self.player_next_shapes = [self.player_bag.get_next() for shape in range(3)]
        self.ai_next_shapes = [self.player_bag.get_next() for shape in range(3)]

        # components (left player, right AI)
        self.player_game = Game(self.get_player_next_shape, self.update_player_score)
        self.ai_game = Game(self.get_ai_next_shape, self.update_ai_score)

        self.player_preview = Preview(self.player_next_shapes, topleft=(PADDING, PADDING))
        self.ai_preview = Preview(self.ai_next_shapes, topleft=(WINDOW_WIDTH//2 + PADDING, PADDING))

        self.state = 'start'

    def get_state_vector(self, board, piece_type):
        flat_board = [cell for row in board for cell in row]
        piece_index = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'].index(piece_type)
        one_hot_piece = [1 if i == piece_index else 0 for i in range(7)]
        state = flat_board + one_hot_piece
        return torch.tensor(state, dtype=torch.float32)

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
        # init bags
        self.player_bag = BagGenerator()
        self.player_next_shapes = [self.player_bag.get_next() for _ in range(3)]

        self.ai_bag = BagGenerator()
        self.ai_next_shapes = [self.ai_bag.get_next() for _ in range(3)]

        # Positions
        player_gamefield_pos = (PADDING + SIDEBAR_WIDTH + PADDING, PADDING)
        player_sidebar_pos = (PADDING, PADDING)

        ai_gamefield_pos = (player_gamefield_pos[0] + GAME_WIDTH + PADDING * 2, PADDING)
        ai_sidebar_pos = (ai_gamefield_pos[0] + GAME_WIDTH + PADDING, PADDING)

        # init game
        self.player_game = Game(self.get_player_next_shape, self.update_player_score, topleft=player_gamefield_pos)
        self.ai_game = Game(self.get_ai_next_shape, self.update_ai_score, topleft=ai_gamefield_pos)

        self.player_game.accept_input = True
        self.ai_game.accept_input = False

        # init preview
        self.player_preview = Preview(self.player_next_shapes, topleft=player_sidebar_pos)
        self.ai_preview = Preview(self.ai_next_shapes, topleft=ai_sidebar_pos)

        # init score
        self.player_score = Score(topleft=(PADDING, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION + PADDING * 2))  # below preview
        self.ai_score = Score(topleft=(ai_sidebar_pos[0], GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION + PADDING * 2))

    def run(self):
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if self.state == 'start' and event.type == pygame.KEYDOWN:
                    self.reset_game()
                    self.state = 'playing'
                    self.input_blocked_until = pygame.time.get_ticks() + 200
                if self.state == 'game_over' and event.type == pygame.KEYDOWN:
                    self.reset_game()
                    self.state = 'playing'
                    self.input_blocked_until = pygame.time.get_ticks() + 200

            self.display_surface.fill(GRAY)

            if self.state == 'start':
                draw_start_screen(self.display_surface)
            
            elif self.state == 'playing':
                # block input for 200ms after start
                if pygame.time.get_ticks() < self.input_blocked_until:
                    self.player_game.run([])  # ignore input
                else:
                    self.player_game.run(events)
                
                self.ai_game.run([])
                current_time = pygame.time.get_ticks()

                if not self.ai_game.game_over and current_time - self.last_ai_move_time > self.ai_move_delay:
                    piece_type = self.ai_game.tetromino.shape
                    board = [[1 if cell else 0 for cell in row] for row in self.ai_game.field_data]
                    
                    # get current state
                    state = self.get_state_vector(board, piece_type).unsqueeze(0)
                    
                    # predict Q-values
                    with torch.no_grad():
                        q_values = self.policy_net(state)

                    # get valid actions
                    valid_actions = get_valid_actions(piece_type, board)
                    valid_indices = [rotation * 10 + x for rotation, x in valid_actions]

                    if valid_indices:
                        # pick action with the highest Q-value
                        action_index = max(valid_indices, key=lambda i: q_values[0][i])

                        # decode action to (rotation, x)
                        rot_idx = action_index // 10
                        x_pos = action_index % 10

                        # apply the action
                        self.ai_game.apply_action(piece_type, rot_idx, x_pos)
                        
                        # get next state
                        next_board = [[1 if cell else 0 for cell in row] for row in self.ai_game.field_data]
                        next_piece = self.ai_game.tetromino.shape
                        next_state = self.get_state_vector(next_board, next_piece)

                        # reward function
                        reward = evaluate_board(next_board) - evaluate_board(board)

                        # Add small bonus for clearing lines
                        if self.ai_game.lines_cleared_this_turn > 0:
                            reward += self.ai_game.lines_cleared_this_turn * 0.5

                        # Add penalty for dying
                        if self.ai_game.game_over:
                            reward -= 2.0

                        # store transition
                        done = self.ai_game.game_over
                        self.replay_memory.push(state.squeeze(), action_index, reward, next_state, done)

                        # train
                        loss = train_step(self.policy_net, self.target_net, self.replay_memory, self.optimizer, batch_size=self.batch_size)
                        if loss is not None:
                            print(f"[Step] Loss: {loss:.4f}")
                        self.last_ai_move_time = current_time

                self.player_score.run()
                self.ai_score.run()

                self.player_preview.run()
                self.ai_preview.run()

                # if self.player_game.game_over or self.ai_game.game_over:
                if self.ai_game.game_over: # remove player condition for training
                    self.state = 'game_over'
            elif self.state == 'game_over':
                self.reset_game()
                self.state = 'playing'
                self.input_blocked_until = pygame.time.get_ticks() + 200


            pygame.display.update()
            self.clock.tick()

if __name__ == '__main__':
    main = Main()
    main.run()