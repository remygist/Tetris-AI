from settings import *
from os.path import join

def draw_game_over_screen(surface, score):
    # fonts
    font = pygame.font.Font(join('assets','Russo_One.ttf'), 48)
    small_font = pygame.font.Font(join('assets','Russo_One.ttf'), 36)

    # text
    game_over_text = font.render("Game Over", True, 'red')
    score_text = small_font.render(f"Final Score: {score}", True, 'white')
    restart_text = small_font.render("Press any key to play again", True, 'white')
    
    surface.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50)))
    surface.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))
    surface.blit(restart_text, restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))

    