import pygame
from settings import *
from os.path import join
from interface.start_screen import Button

def draw_stats_screen(main_instance, surface):
    # fonts
    title_font  = pygame.font.Font(join('assets','Russo_One.ttf'), 64)
    header_font = pygame.font.Font(join('assets','Russo_One.ttf'), 36)
    text_font   = pygame.font.Font(join('assets','Russo_One.ttf'), 28)

    # background
    surface.fill((20, 20, 20))

    # main Title
    title_surf = title_font.render("Statistics", True, 'white')
    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, 60))
    surface.blit(title_surf, title_rect)

    # column headers
    col1_x = WINDOW_WIDTH // 4
    col2_x = WINDOW_WIDTH * 3 // 4
    y_col = title_rect.bottom + 20
    player_hdr = header_font.render("Player", True, 'lightblue')
    ai_hdr = header_font.render("AI",     True, 'lightblue')
    surface.blit(player_hdr, player_hdr.get_rect(center=(col1_x, y_col)))
    surface.blit(ai_hdr,     ai_hdr.get_rect(center=(col2_x, y_col)))

    # fetch stats
    stats = main_instance.stats
    history = stats.get('history', [])
    games = stats.get('games_played', 0)
    count = max(games, 1) # avoid divide by zero

    # last-game data
    if history:
        last = history[-1]
    else:
        last = {
            'player_score': 0,    'ai_score': 0,
            'player_moves': 0,    'ai_moves': 0,
            'player_lines': 0,    'ai_lines': 0,
            'player_holes': 0,    'ai_holes': 0,
            'player_tetrises': 0, 'ai_tetrises': 0
        }

    # section: last game
    y_section = y_col + header_font.get_height() + 20
    last_title = header_font.render("Last Game", True, (255, 215, 0))
    last_rect  = last_title.get_rect(center=(WINDOW_WIDTH//2, y_section))
    surface.blit(last_title, last_rect)

    line_h = text_font.get_height() + 10
    y_values = last_rect.bottom + 10

    # player stats
    pl_texts = [
        f"Score: {last['player_score']}",
        f"Moves: {last['player_moves']}",
        f"Lines: {last['player_lines']}",
        f"Holes: {last['player_holes']}",
        f"Tetrises: {last['player_tetrises']}"
    ]
    for i, txt in enumerate(pl_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col1_x, y_values + i * line_h))
        surface.blit(surf, rect)

    # ai stats
    ai_texts = [
        f"Score: {last['ai_score']}",
        f"Moves: {last['ai_moves']}",
        f"Lines: {last['ai_lines']}",
        f"Holes: {last['ai_holes']}",
        f"Tetrises: {last['ai_tetrises']}"
    ]
    for i, txt in enumerate(ai_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col2_x, y_values + i * line_h))
        surface.blit(surf, rect)

    # section: averages
    y_avg_section = y_values + max(len(pl_texts), len(ai_texts)) * line_h + 40
    avg_title = header_font.render("Average/Game", True, (0, 255, 127))
    avg_rect  = avg_title.get_rect(center=(WINDOW_WIDTH//2, y_avg_section))
    surface.blit(avg_title, avg_rect)

    # calculate averages
    avg_player_score = stats.get('total_player_score', 0) / count if stats.get('total_player_score') else 0
    avg_player_moves = stats.get('total_player_moves', 0) / count
    avg_player_lines = stats.get('total_player_lines', 0) / count
    avg_player_holes = stats.get('total_player_holes', 0) / count
    avg_player_tets = stats.get('total_player_tetrises',0) / count
    avg_ai_score = stats.get('total_ai_score', 0) / count if stats.get('total_ai_score') else 0
    avg_ai_moves = stats.get('total_ai_moves', 0) / count
    avg_ai_lines = stats.get('total_ai_lines', 0) / count
    avg_ai_holes = stats.get('total_ai_holes', 0) / count
    avg_ai_tets  = stats.get('total_ai_tetrises', 0) / count

    y_avg_values = avg_rect.bottom + 10

    # player averages
    p_avg_texts = [
        f"Score/Games: {avg_player_score:.1f}",
        f"Moves/Games: {avg_player_moves:.1f}",
        f"Lines/Games: {avg_player_lines:.1f}",
        f"Holes/Games: {avg_player_holes:.1f}",
        f"Tets/Games:  {avg_player_tets:.1f}"
    ]
    for i, txt in enumerate(p_avg_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col1_x, y_avg_values + i * line_h))
        surface.blit(surf, rect)

    # ai averages
    ai_avg_texts = [
        f"Score/Games: {avg_ai_score:.1f}",
        f"Moves/Games: {avg_ai_moves:.1f}",
        f"Lines/Games: {avg_ai_lines:.1f}",
        f"Holes/Games: {avg_ai_holes:.1f}",
        f"Tets/Games:  {avg_ai_tets:.1f}"
    ]
    for i, txt in enumerate(ai_avg_texts):
        surf = text_font.render(txt, True, 'white')
        rect = surf.get_rect(center=(col2_x, y_avg_values + i * line_h))
        surface.blit(surf, rect)

    # buttons
    def go_back():
        main_instance.state = 'game_over'

    def reset_stats():
        main_instance.stats = main_instance.init_stats()
        main_instance.state = 'main_menu'

    back_btn = Button("Back", (150, WINDOW_HEIGHT - 60), text_font, action=go_back)
    reset_btn = Button("Reset Stats", (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 60), text_font, action=reset_stats)
    back_btn.draw(surface)
    reset_btn.draw(surface)

    return [back_btn, reset_btn]
