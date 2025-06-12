import pygame
from settings import *
from os.path import join
from interface.start_screen import Button  # Reuse the Button class

def draw_stats_screen(main_instance, surface):
    """
    Draws a two-column Stats screen:
    - Left column: Player stats
    - Right column: AI stats
    Shows “Last Game” and “Average” sections.
    """
    # Fonts
    title_font  = pygame.font.Font(join('assets','Russo_One.ttf'), 64)
    header_font = pygame.font.Font(join('assets','Russo_One.ttf'), 36)
    text_font   = pygame.font.Font(join('assets','Russo_One.ttf'), 28)

    # Background
    surface.fill((20, 20, 20))

    # Main Title
    title_surf = title_font.render("Statistics", True, 'white')
    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, 60))
    surface.blit(title_surf, title_rect)

    # Column headers (Player / AI)
    col1_x = WINDOW_WIDTH // 4
    col2_x = WINDOW_WIDTH * 3 // 4
    y_col = title_rect.bottom + 20
    player_hdr = header_font.render("Player", True, 'lightblue')
    ai_hdr     = header_font.render("AI",     True, 'lightblue')
    player_rect = player_hdr.get_rect(center=(col1_x, y_col))
    ai_rect     = ai_hdr.get_rect(center=(col2_x, y_col))
    surface.blit(player_hdr, player_rect)
    surface.blit(ai_hdr,     ai_rect)

    # Fetch stats
    stats   = main_instance.stats
    history = stats.get('history', [])
    games   = stats.get('games_played', 0)
    count   = max(games, 1)

    # Last-game data
    if history:
        last = history[-1]
    else:
        last = {
            'player_score': 0, 'ai_score': 0,
            'player_moves': 0, 'player_lines': 0,
            'ai_moves': 0,     'ai_lines': 0
        }

    # Section: Last Game
    y_section = y_col + header_font.get_height() + 20
    last_title = header_font.render("Last Game", True, (255, 215, 0))
    last_rect  = last_title.get_rect(center=(WINDOW_WIDTH//2, y_section))
    surface.blit(last_title, last_rect)

    line_h = text_font.get_height() + 10
    y_values = last_rect.bottom + 10

    # Player Last Game values
    pl_texts = [
        f"Score: {last['player_score']}",
        f"Moves: {last['player_moves']}",
        f"Lines: {last['player_lines']}",
    ]
    for i, txt in enumerate(pl_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col1_x, y_values + i * line_h))
        surface.blit(surf, rect)

    # AI Last Game values
    ai_texts = [
        f"Score: {last['ai_score']}",
        f"Moves: {last['ai_moves']}",
        f"Lines: {last['ai_lines']}",
    ]
    for i, txt in enumerate(ai_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col2_x, y_values + i * line_h))
        surface.blit(surf, rect)

    # Section: Averages
    y_avg_section = y_values + max(len(pl_texts), len(ai_texts)) * line_h + 40
    avg_title = header_font.render("Average", True, (0, 255, 127))
    avg_rect  = avg_title.get_rect(center=(WINDOW_WIDTH//2, y_avg_section))
    surface.blit(avg_title, avg_rect)

    # Compute averages
    avg_player_score = stats.get('total_player_score', 0) / count if stats.get('total_player_score') else 0
    avg_player_moves = stats.get('total_player_moves', 0) / count
    avg_player_lines = stats.get('total_player_lines', 0) / count
    avg_ai_score     = stats.get('total_ai_score', 0) / count if stats.get('total_ai_score') else 0
    avg_ai_moves     = stats.get('total_ai_moves', 0) / count
    avg_ai_lines     = stats.get('total_ai_lines', 0) / count

    y_avg_values = avg_rect.bottom + 10

    # Player Averages
    p_avg_texts = [
        f"Score/Game: {avg_player_score:.1f}",
        f"Moves/Game: {avg_player_moves:.1f}",
        f"Lines/Game: {avg_player_lines:.1f}",
    ]
    for i, txt in enumerate(p_avg_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col1_x, y_avg_values + i * line_h))
        surface.blit(surf, rect)

    # AI Averages
    ai_avg_texts = [
        f"Score/Game: {avg_ai_score:.1f}",
        f"Moves/Game: {avg_ai_moves:.1f}",
        f"Lines/Game: {avg_ai_lines:.1f}",
    ]
    for i, txt in enumerate(ai_avg_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col2_x, y_avg_values + i * line_h))
        surface.blit(surf, rect)

    # Buttons
    def go_back():
        main_instance.state = 'game_over'

    def reset_stats():
        main_instance.stats = main_instance.init_stats()
        main_instance.state = 'main_menu'

    back_btn  = Button("Back",        (150, WINDOW_HEIGHT - 60), text_font, action=go_back)
    back_btn.draw(surface)

    return back_btn
