from settings import *
from sys import exit


# components
from game import Game
from score import Score
from preview import Preview
from interface.start_screen import draw_start_screen
from interface.game_over_screen import draw_game_over_screen


from random import choice

class Main:
    def __init__(self):

        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Tetris')

        # shapes
        self.next_shapes = [choice(list(TETROMINOS.keys())) for shape in range(3)]

        # components
        self.game = Game(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview(self.next_shapes)
        self.state = 'start'

    def update_score(self, lines, score, level):
        self.score.lines = lines
        self.score.score = score
        self.score.level = level

    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(TETROMINOS.keys())))
        return next_shape

    def reset_game(self):
        self.next_shapes = [choice(list(TETROMINOS.keys())) for _ in range(3)]
        self.game = Game(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview(self.next_shapes)


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                if self.state == 'start' and event.type == pygame.KEYDOWN:
                    self.reset_game()
                    self.state = 'playing'
                
                if self.state == 'game_over' and event.type == pygame.KEYDOWN:
                    self.reset_game()
                    self.state = 'playing'

            # display
            self.display_surface.fill(GRAY)

            if self.state == 'start':
                draw_start_screen(self.display_surface)
            elif self.state == 'playing':
                self.game.run()
                self.score.run()
                self.preview.run()

                if self.game.game_over:
                    self.state = 'game_over'
                    
            elif self.state == 'game_over':
                draw_game_over_screen(self.display_surface, self.score.score)

            # updating game
            pygame.display.update()
            self.clock.tick()


if __name__ == '__main__':
    main = Main()
    main.run()