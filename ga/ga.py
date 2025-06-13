import random
from ai_controller import pick_best_action
import json
import matplotlib.pyplot as plt 
import time


# genetic algorithm config
POPULATION_SIZE = 30
NUM_GENERATIONS = 30
MUTATION_RATE = 0.2
TOURNAMENT_SIZE = 5
ELITE_COUNT = 3
GENE_LENGTH = 8
WEIGHT_MIN = -10
WEIGHT_MAX = 10


def generate_individual():
    return [random.uniform(WEIGHT_MIN, WEIGHT_MAX) for _ in range(GENE_LENGTH)]

def mutate(individual):
    return [
        gene + random.uniform(-1, 1) if random.random() < MUTATION_RATE else gene
        for gene in individual
    ]

def crossover(parent1, parent2):
    return [
        random.choice([g1, g2]) for g1, g2 in zip(parent1, parent2)
    ]

def tournament_selection(population, fitnesses):
    candidates = random.sample(list(zip(population, fitnesses)), TOURNAMENT_SIZE)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def evaluate_individual(main_class, weights):
    main_class.reset_game()
    main_class.ai_game.set_ai_weights(weights)

    max_steps = 1000 # stop the test early for speed
    steps = 0

    while not main_class.ai_game.game_over and steps < max_steps:
        piece_type = main_class.ai_game.tetromino.shape
        board = [[1 if cell else 0 for cell in row] for row in main_class.ai_game.field_data]
        action = pick_best_action(piece_type, board, weights)
        if action:
            rot_idx, x_pos = action
            main_class.ai_game.apply_action(piece_type, rot_idx, x_pos)
        steps += 1

    return main_class.ai_score.lines + 0.1 * steps

def run_ga(main_class):
    fitness_history = []
    run_id = int(time.time())
    population = [generate_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(NUM_GENERATIONS):
        print(f"\n--- Generation {generation} ---")
        fitnesses = [evaluate_individual(main_class, ind) for ind in population]

        best_fitness = max(fitnesses)
        fitness_history.append(best_fitness)
        best_individual = population[fitnesses.index(best_fitness)]
        print(f"Best fitness: {best_fitness:.2f}, weights: {best_individual}")

        sorted_pop = [x for _, x in sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)]
        new_population = sorted_pop[:ELITE_COUNT]

        while len(new_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population, fitnesses)
            parent2 = tournament_selection(population, fitnesses)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)

        population = new_population
    plot_curve(run_id, fitness_history)
    final_fitnesses = [evaluate_individual(main_class, ind) for ind in population]
    best = population[final_fitnesses.index(max(final_fitnesses))]

    
    filename = f"saved_weights/best_weights_{run_id}.json"
    with open(filename, "w") as f:
        json.dump(best, f)
    print(f"\n🎯 Final best weights: {best}")
    return best

def plot_curve(run_id, fitness_history):
    plt.figure()
    plt.plot(range(1, NUM_GENERATIONS + 1), fitness_history)
    plt.xlabel("Generation")
    plt.ylabel("Best fitness (lines cleared)")
    plt.title("GA progress")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"fitness_history/fitness_history_{run_id}.png")                          
    print("📈  Fitness plot saved as fitness_history.png")
