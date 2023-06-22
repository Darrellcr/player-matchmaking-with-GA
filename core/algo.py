from __future__ import annotations
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import random
from time import perf_counter

from core.object import Team, Individual, Player, Role


@dataclass
class Generation:
    population: list[Individual]
    player_pool: set[Player]
    generation_number: int = field(default=0, init=False)

    def next_generation(self):
        self.generation_number += 1
        new_population = []
        current_population_size = len(self.population)
        
        while len(new_population) < current_population_size:
            parent1, parent2 = self.roulette_wheel_selection()
            offspring1, offspring2 = parent1.pmx_crossover(parent2)
            offspring1.mutate(self.player_pool)
            offspring2.mutate(self.player_pool)

            if len(new_population) < current_population_size-1: 
                new_population.append(offspring1)
                new_population.append(offspring2)
                continue
            # handle odd population size
            random_offspring = random.choice([offspring1, offspring2])
            new_population.append(random_offspring)

        self.population = new_population

    def roulette_wheel_selection(self) -> tuple[Individual, Individual]:
        population_fitness = [individual.calculate_fitness() for individual in self.population]
        total_fitness = sum(population_fitness)
        probabilities = [fitness / total_fitness for fitness in population_fitness]
        # indexes = [i for i, _ in enumerate(self.population)]
        # selected_parent_index = random.choices(indexes, weights=probabilities, k=1)[0]
        # selected_parent = self.population.pop(selected_parent_index)
        selected_parent1 = random.choices(self.population, weights=probabilities, k=1)[0]
        selected_parent2 = random.choices(self.population, weights=probabilities, k=1)[0]
        return selected_parent1, selected_parent2
        # return selected_parent

    def get_best_individual(self) -> Individual:
        return max(enumerate(self.population), key=lambda x: x[1].calculate_fitness())

    def get_best_individual_fitness(self) -> int:
        return max(individual.calculate_fitness() for individual in self.population)
    
    def get_worst_individual_fitness(self) -> int:
        return min(individual.calculate_fitness() for individual in self.population)
    
    def count_player_in_population(self) -> int:
        players = set()
        for individual in self.population:
            for player in individual.team1.players:
                players.add(player)
            for player in individual.team2.players:
                players.add(player)
        return len(players)
    

def main():
    start = perf_counter()
    player_pool: set[Player] = Player.generate_player_pool(1000)
    inputted_player = Player(1400, Role.GOLDLANE, is_inputted=True)
    team_pool = Team.generate_team_pool(player_pool, inputted_player=inputted_player)
    population = Individual.generate_population(team_pool)
    generation = Generation(population, player_pool)
    best_fitness_over_time = []
    worst_fitness_over_time = []

    for _ in range(30):
        # print(f"Generation: {generation.generation_number}")
        # print(f"-- Player count: {generation.player_count()}, {len(generation.player_pool)}")
        best_fitness_over_time.append(generation.get_best_individual_fitness())
        worst_fitness_over_time.append(generation.get_worst_individual_fitness())
        generation.next_generation()
    # print(f"Generation: {generation.generation_number}")
    # print(f"-- Player count: {generation.player_count()}, {len(generation.player_pool)}")
    best_fitness_over_time.append(generation.get_best_individual_fitness())
    worst_fitness_over_time.append(generation.get_worst_individual_fitness())
    end = perf_counter()
    print(f"Time taken: {end-start:.2f}s")

    idx, best_individual = generation.get_best_individual()
    print(idx)
    print('----------------Team 1----------------')
    for player in best_individual.team1.players:
        print(player)
    print('----------------Team 2----------------')
    for player in best_individual.team2.players:
        print(player)
    
    fig, ax = plt.subplots(2, 1)
    ax[0].set_title("Best fitness over time")
    ax[0].plot(best_fitness_over_time)
    ax[1].set_title("Worst fitness over time")
    ax[1].plot(worst_fitness_over_time)
    plt.show()        


if __name__ == "__main__":
    main()