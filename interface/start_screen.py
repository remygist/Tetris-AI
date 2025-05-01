from settings import *
from os.path import join

def draw_start_screen(surface):
    # fonts
    font = pygame.font.Font(join('assets','Russo_One.ttf'), 48)

    # text
    text = font.render("Press any key to start", True, 'white')
    
    rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    surface.blit(text, rect)