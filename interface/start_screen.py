import pygame
from settings import *
from os.path import join
pygame.font.init()
from models.dqn_model import set_agent_model

class Button:
    def __init__(self, text, center, font, action=None):
        self.text = text
        self.font = font
        self.action = action
        self.color = 'white'
        self.hover_color = 'lightgray'
        self.text_surface = self.font.render(self.text, True, self.color)
        self.rect = self.text_surface.get_rect(center=center)
        


    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hover else self.color
        self.text_surface = self.font.render(self.text, True, color)
        surface.blit(self.text_surface, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

def start_game(main_instance):
    main_instance.state = 'difficulty_select'
    main_instance.input_blocked_until = pygame.time.get_ticks() + 300


def quit_game():
    pygame.quit()
    exit()

def show_credits():
    print("Created by Your Name - Your School")

def draw_start_screen(main_instance, surface):
    background_image = pygame.image.load(join('assets', 'background.png')).convert()
    surface.blit(background_image, (0,0))

    # fonts
    title_font = pygame.font.Font(join('assets', 'Russo_One.ttf'), 72)
    menu_font = pygame.font.Font(join('assets', 'Russo_One.ttf'), 36)
    
    # title
    title_text = title_font.render("Tetris AI", True, 'white')
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
    surface.blit(title_text, title_rect)

    # buttons
    play_button = Button("Play", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), menu_font, action=lambda: start_game(main_instance))
    quit_button = Button("Quit", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60), menu_font, action=quit_game)
    credits_button = Button("Credits", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120), menu_font, action=show_credits)

    buttons = [play_button, quit_button, credits_button]
    for button in buttons:
        button.draw(surface)

    return buttons

def draw_difficulty_screen(main_instance, surface):
    # Load and draw background
    background_image = pygame.image.load(join('assets', 'background.png')).convert()
    surface.blit(background_image, (0, 0))

    # Fonts
    title_font = pygame.font.Font(join('assets', 'Russo_One.ttf'), 64)
    menu_font = pygame.font.Font(join('assets', 'Russo_One.ttf'), 36)

    # Title
    title_text = title_font.render("Select Difficulty", True, 'white')
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
    surface.blit(title_text, title_rect)

    # Define actions for each difficulty
    def set_easy():
        main_instance.difficulty = 'easy'
        main_instance.agent = set_agent_model('easy')
        main_instance.reset_game()
        main_instance.state = 'playing'
        main_instance.input_blocked_until = pygame.time.get_ticks() + 200

    def set_medium():
        """main_instance.difficulty = 'medium'
        main_instance.agent = set_agent_model('medium')
        main_instance.reset_game()
        main_instance.state = 'playing'
        main_instance.input_blocked_until = pygame.time.get_ticks() + 200"""
        print("medium")

    def set_hard():
        """main_instance.difficulty = 'hard'
        main_instance.agent = set_agent_model('hard')
        main_instance.reset_game()
        main_instance.state = 'playing'
        main_instance.input_blocked_until = pygame.time.get_ticks() + 200"""
        print("hard")

    # Create difficulty buttons
    easy_button = Button("Easy", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40), menu_font, action=set_easy)
    medium_button = Button("Medium", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20), menu_font, action=set_medium)
    hard_button = Button("Hard", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80), menu_font, action=set_hard)

    buttons = [easy_button, medium_button, hard_button]

    # Draw buttons
    for button in buttons:
        button.draw(surface)

    return buttons

