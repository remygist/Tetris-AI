import pygame
from settings import *
from os.path import join
from interface.start_screen import Button  # Reuse the Button class

def draw_game_over_screen(main_instance, surface):
    # fonts
    title_font = pygame.font.Font(join('assets','Russo_One.ttf'), 64)
    menu_font = pygame.font.Font(join('assets','Russo_One.ttf'), 36)

    # Background
    surface.fill((20, 20, 20))  # dark background

    # Game Over title
    game_over_text = title_font.render("Game Over", True, 'red')
    surface.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)))

    # Final score
    score_text = menu_font.render(f"Final Score: {main_instance.player_score.score}", True, 'white')
    surface.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4 + 60)))

    # Buttons
    def restart():
        main_instance.reset_game()
        main_instance.state = 'playing'
        main_instance.input_blocked_until = pygame.time.get_ticks() + 200

    def back_to_menu():
        main_instance.reset_game()
        main_instance.state = 'main_menu'

    def view_stats():
        main_instance.state = 'stats'

    def quit_game():
        main_instance.save_stats()
        pygame.quit()
        exit()

    # Create buttons
    buttons = [
        Button("Play Again", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), menu_font, action=restart),
        Button("Back to Menu", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60), menu_font, action=back_to_menu),
        Button("View Stats", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120), menu_font, action=view_stats),
        Button("Quit", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 180), menu_font, action=quit_game),
    ]

    # Draw buttons
    for button in buttons:
        button.draw(surface)

    return buttons
