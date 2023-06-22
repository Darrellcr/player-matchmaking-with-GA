from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
import random


class Role(Enum):
    GOLDLANE = auto()
    MIDLANE = auto()
    JUNGLE = auto()
    OFFLANE = auto()
    ROAM = auto()


@dataclass(frozen=True)
class Player:
    id_iter = itertools.count(start=1)

    id: int = field(default_factory=lambda: next(Player.id_iter), init=False)
    mmr: int
    most_played_role: Role
    is_inputted: bool = field(default=False)

    @classmethod
    def generate_player_pool(cls, size: int, mean: int = 1800, std: int = 400) -> set[Player]:
        player_pool: set[Player] = set()
        roles = tuple(Role)
        for _ in range(size):
            player = cls(
                mmr=int(random.gauss(mean, std)),
                most_played_role=random.choices(roles, weights=[1 for _ in range(len(roles))], k=1)[0],
            )
            player_pool.add(player)
        return player_pool


@dataclass
class Team:
    players: list[Player]

    @classmethod
    def generate_team_pool(cls, player_pool: set[Player], percentage: float = 0.9, inputted_player: Player = None) -> list[Team]:
        if inputted_player is not None:
            player_pool.add(inputted_player)

        temp_player_pool = player_pool.copy()
        number_of_teams = cls._calculate_number_of_team(
            len(player_pool), percentage)
        team_pool: list[Team] = []
        for _ in range(number_of_teams):
            team = cls([temp_player_pool.pop() for _ in range(5)])
            team_pool.append(team)

        return team_pool

    @staticmethod
    def _calculate_number_of_team(number_of_player, percentage):
        number_of_teams = int(number_of_player * percentage) // 5
        is_even = number_of_teams % 2 == 0
        if is_even:
            return number_of_teams
        return number_of_teams - 1

    def calculate_mmr_mean(self) -> float:
        return sum(player.mmr for player in self.players) / len(self.players)

    def calculate_mmr_std(self) -> float:
        mean = self.calculate_mmr_mean()
        variance = sum((player.mmr - mean)**2
                       for player in self.players) / len(self.players)
        return math.sqrt(variance)

    def contains_inputted_player(self) -> bool:
        return any(player.is_inputted for player in self.players)

    def count_distinct_role(self) -> int:
        return len(set(player.most_played_role for player in self.players))
    
    def mutate(self, both_team_players, player_pool: set[Player], mutation_rate: float) -> None:
        for i, player in enumerate(self.players):
            if random.random() >= mutation_rate:
                continue

            popped_player = player_pool.pop()
            is_popped_player_legal = popped_player not in both_team_players
            while not is_popped_player_legal:
                player_pool.add(popped_player)
                popped_player = player_pool.pop()
                is_popped_player_legal = popped_player not in both_team_players


            self.players[i] = popped_player
            player_pool.add(popped_player)

    def print_players(self) -> None:
        for player in self.players:
            print(player)


@dataclass
class Individual:
    team1: Team
    team2: Team

    @classmethod
    def generate_population(cls, team_pool: list[Team]) -> list[Individual]:
        population_size = len(team_pool) // 2
        population = [cls(team_pool.pop(), team_pool.pop())
                      for _ in range(population_size)]
        return population

    def calculate_fitness(self):
        '''
        1. team std
        2. number of distinct role
        3. mmr diff between team
        4. player inputan atau bukan
        '''
        fitness1 = 1100
        fitness1 -= self.team1.calculate_mmr_std() ** 1.25 / 2
        fitness1 -= self.team2.calculate_mmr_std() ** 1.25 / 2
        fitness1 = max(fitness1, 0)

        fitness2 = 0
        fitness2 += (self.team1.count_distinct_role() - 1) * 120
        fitness2 += (self.team2.count_distinct_role() - 1) * 120

        fitness3 = 1500
        fitness3 -= abs(self.team1.calculate_mmr_mean() -
                        self.team2.calculate_mmr_mean()) ** 1.5
        fitness3 = max(fitness3, 0)

        fitness_score = fitness1 + fitness2 + fitness3
        if self.team1.contains_inputted_player() or self.team2.contains_inputted_player():
            fitness_score += 4000

        return max(fitness_score, 1)

    def pmx_crossover(self, other: Individual) -> tuple[Individual, Individual]:
        def split_parent(parent: Individual, crossover_point: int) -> tuple[list[Player], list[Player]]:
            parent = parent.team1.players + parent.team2.players
            parent_left = parent[:crossover_point]
            parent_right = parent[crossover_point:]
            return parent_left, parent_right

        def generate_legal_offspring(
            offspring1_left: list[Player],
            offspring1_right: list[Player],
            offspring2_right: list[Player]
        ) -> Individual:
            legal_offspring = ([None] * len(offspring1_left)
                               ) + offspring1_right
            offspring1_right_player_ids = tuple(
                player.id for player in offspring1_right)

            for i, player in enumerate(offspring1_left):
                legal_player = player
                is_player_legal = legal_player.id not in offspring1_right_player_ids
                while not is_player_legal:
                    legal_player = offspring2_right[offspring1_right.index(
                        legal_player)]
                    is_player_legal = legal_player.id not in offspring1_right_player_ids
                legal_offspring[i] = legal_player

            return Individual.from_array(legal_offspring)

        crossover_point = random.randint(1, len(self.team1.players)*2 - 1)

        parent1_left, parent1_right = split_parent(self, crossover_point)
        parent2_left, parent2_right = split_parent(other, crossover_point)

        offspring1 = generate_legal_offspring(
            parent1_left, parent2_right, parent1_right)
        offspring2 = generate_legal_offspring(
            parent2_left, parent1_right, parent2_right)

        return offspring1, offspring2

    @classmethod
    def from_array(cls, array: list[Player]) -> Individual:
        team1 = Team(array[:5])
        team2 = Team(array[5:])
        return cls(team1, team2)

    def mutate(self, player_pool: set[Player], mutation_rate: float = 0.01) -> None:
        both_team_players = self.team1.players + self.team2.players
        self.team1.mutate(both_team_players, player_pool, mutation_rate)
        self.team2.mutate(both_team_players, player_pool, mutation_rate)

def check_player_mmr_distribution() -> None:
    player_pool = list(Player.generate_player_pool(1000))
    mmr = np.array([player.mmr for player in player_pool])
    plt.hist(mmr, bins=50)
    plt.show()


def test_mutation():
    player_pool: set[Player] = Player.generate_player_pool(1000)
    team_pool = Team.generate_team_pool(player_pool)

    population = Individual.generate_population(team_pool)

    print('Team 1')
    population[0].team1.print_players()
    print('Team 2')
    population[0].team2.print_players()
    population[0].mutate(player_pool=player_pool)
    print()
    print('Team 1')
    population[0].team1.print_players()
    print('Team 2')
    population[0].team2.print_players()


def test_crossover():
    player_pool: set[Player] = Player.generate_player_pool(1000)
    team_pool = Team.generate_team_pool(player_pool)

    population = Individual.generate_population(team_pool)

    print('Parent 1 Team 1')
    population[0].team1.print_players()
    print('Parent 1 Team 2')
    population[0].team2.print_players()
    offspring1, offspring2 = population[0].crossover(population[1])
    print('offspring 1 Team 1')
    offspring1.team1.print_players()
    print('offspring 1 Team 2')
    offspring1.team2.print_players()


def test_fitness():
    player_pool: set[Player] = Player.generate_player_pool(1000)
    team_pool = Team.generate_team_pool(player_pool)

    population = Individual.generate_population(team_pool)

    min_fitness = min(individual.calculate_fitness()
                      for individual in population)
    max_fitness = max(individual.calculate_fitness()
                      for individual in population)

    print(f'{min_fitness=}')
    print(f'{max_fitness=}')

    max_pos = None
    max_fitness = 0
    for idx, individual in enumerate(population):
        if max_pos is None:
            max_pos = idx
            max_fitness = individual.calculate_fitness()
        elif individual.calculate_fitness() > max_fitness:
            max_pos = idx
            max_fitness = individual.calculate_fitness()

    individual: Individual = population[max_pos]
    print('Team 1')
    for player in individual.team1.players:
        print(f'{player}')
    print('Team 2')
    for player in individual.team2.players:
        print(f'{player}')
    mmr_mean_diff = abs(individual.team1.calculate_mmr_mean() -
                   individual.team2.calculate_mmr_mean())
    max_fitness = individual.calculate_fitness()
    print(f'{max_fitness=:.2f}')
    print(f'{mmr_mean_diff=:.2f}')
    print(f'{individual.team1.count_distinct_role()=}')
    print(f'{individual.team1.calculate_mmr_std()=:.2f}')
    print(f'{individual.team2.count_distinct_role()=}')
    print(f'{individual.team2.calculate_mmr_std()=:.2f}')


if __name__ == "__main__":
    test_fitness()
