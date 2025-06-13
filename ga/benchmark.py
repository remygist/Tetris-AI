import os
import json
from main import Main
from ai_controller import pick_best_action

NUM_TEST_GAMES = 5  
WEIGHTS_FOLDER = "saved_weights"


def evaluate_weights(weights):
    total_lines = 0
    total_score = 0
    for _ in range(NUM_TEST_GAMES):
        main = Main()
        main.reset_game()
        main.ai_game.set_ai_weights(weights)

        max_steps = 1000
        steps = 0

        while not main.ai_game.game_over and steps < max_steps:
            piece_type = main.ai_game.tetromino.shape
            board = [[1 if cell else 0 for cell in row] for row in main.ai_game.field_data]
            action = pick_best_action(piece_type, board, weights)
            if action:
                rot_idx, x_pos = action
                main.ai_game.apply_action(piece_type, rot_idx, x_pos)
            steps += 1

        total_lines += main.ai_score.lines
        total_score += main.ai_score.score

    avg_lines = total_lines / NUM_TEST_GAMES
    avg_score = total_score / NUM_TEST_GAMES
    return avg_lines, avg_score

def run_benchmark():
    print("\n Benchmarking saved GA agents...\n")

    results = []
    for filename in sorted(os.listdir(WEIGHTS_FOLDER)):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(WEIGHTS_FOLDER, filename)
        with open(filepath, "r") as f:
            weights = json.load(f)

        avg_lines, avg_score = evaluate_weights(weights)
        results.append((filename, avg_lines, avg_score))
        print(f"{filename}: avg lines = {avg_lines:.2f}, avg score = {avg_score:.2f}")

    print("\n Top Performers by Lines Cleared:")
    for filename, avg_lines, _ in sorted(results, key=lambda x: x[1], reverse=True)[:5]:
        print(f"{filename} -> {avg_lines:.2f} lines")

    print("\n Top Performers by Score:")
    for filename, _, avg_score in sorted(results, key=lambda x: x[2], reverse=True)[:5]:
        print(f"{filename} -> {avg_score:.2f} score")

if __name__ == "__main__":
    run_benchmark()
