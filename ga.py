import random
from ai_controller import pick_best_action
from copy import deepcopy

# genetic algorithm config
POPULATION_SIZE = 30
NUM_GENERATIONS = 200
MUTATION_RATE = 0.2
TOURNAMENT_SIZE = 5
ELITE_COUNT = 3
GENE_LENGTH = 4
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

    max_steps = 500  # stop the test early for speed
    steps = 0

    while not main_class.ai_game.game_over and steps < max_steps:
        piece_type = main_class.ai_game.tetromino.shape
        board = [[1 if cell else 0 for cell in row] for row in main_class.ai_game.field_data]
        action = pick_best_action(piece_type, board, weights)
        if action:
            rot_idx, x_pos = action
            main_class.ai_game.apply_action(piece_type, rot_idx, x_pos)
        steps += 1

    return main_class.ai_score.lines  

def run_ga(main_class):
    population = [generate_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(NUM_GENERATIONS):
        print(f"\n--- Generation {generation} ---")
        fitnesses = [evaluate_individual(main_class, ind) for ind in population]

        best_fitness = max(fitnesses)
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

    final_fitnesses = [evaluate_individual(main_class, ind) for ind in population]
    best = population[final_fitnesses.index(max(final_fitnesses))]
    print(f"\n🎯 Final best weights: {best}")
    return best
