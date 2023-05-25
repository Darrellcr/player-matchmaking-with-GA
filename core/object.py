from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
import itertools
import math
import random


class Role(Enum):
    MARKSMAN = auto()
    MAGE = auto()
    ASSASSIN = auto()
    OFFLANE = auto()
    ROAMER = auto()


@dataclass(frozen=True)
class Player:
    id_iter = itertools.count(start=1)

    id: int = field(default_factory=lambda: next(Player.id_iter), init=False)
    mmr: int
    most_played_role: Role

    @classmethod
    def generate_player_pool(cls, size: int, mean: int = 1000, std: int = 150) -> set[Player]:
        player_pool: set[Player] = set()
        roles = tuple(Role)
        for _ in range(size):
            player = cls(
                mmr=int(random.gauss(mean, std)),
                most_played_role=random.choice(roles),
            )
            player_pool.add(player)
        return player_pool


@dataclass
class Team:
    players: list[Player]

    @classmethod
    def generate_team_pool(cls, player_pool: set[Player], percentage: float = 0.9) -> tuple[list[Team], set[Player]]:
        number_of_teams = cls._calculate_number_of_team(len(player_pool), percentage)
        team_pool: list[Team] = []
        for _ in range(number_of_teams):
            team = cls([player_pool.pop() for _ in range(5)])
            team_pool.append(team)
        return team_pool, player_pool
    
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
    
    def count_distinct_role(self) -> int:
        return len(set(player.most_played_role for player in self.players))


@dataclass
class Individual:
    team1: Team
    team2: Team

    @classmethod
    def generate_population(cls, team_pool: list[Team], percentage: float = 0.9) -> list[Individual]:
        population_size = len(team_pool) // 2
        population = [cls(team_pool.pop(), team_pool.pop()) for _ in range(population_size)]
        return population

    def calculate_fitness_function(self):
        pass

    def crossover(self, other: Individual) -> None:
        pass
        
    def mutate(self, remaining_players: set[Player]):
        pass


if __name__ == "__main__":
    player_pool: set[Player] = Player.generate_player_pool(1000)
    team_pool, remaining_players = Team.generate_team(player_pool)


    print(team_pool[1])
