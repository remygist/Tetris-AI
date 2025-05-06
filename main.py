from settings import *
from sys import exit


# components
from game import Game
from score import Score
from preview import Preview
from interface.start_screen import draw_start_screen
from interface.game_over_screen import draw_game_over_screen
from bag_generator import BagGenerator


from random import choice

class Main:
    def __init__(self):

        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Tetris')
        self.input_blocked_until = 0

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
                
                self.ai_game.run([]) # ignore ai input

                self.player_score.run()
                self.ai_score.run()

                self.player_preview.run()
                self.ai_preview.run()

                if self.player_game.game_over or self.ai_game.game_over:
                    self.state = 'game_over'
            elif self.state == 'game_over':
                draw_game_over_screen(self.display_surface, self.player_score.score)

            pygame.display.update()
            self.clock.tick()

if __name__ == '__main__':
    main = Main()
    main.run()