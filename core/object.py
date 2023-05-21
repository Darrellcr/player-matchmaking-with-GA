from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
import itertools
import random


class Role(Enum):
    MARKSMAN = auto()
    MAGE = auto()
    ASSASSIN = auto()
    OFFLANE = auto()
    ROAMER = auto()


@dataclass
class Player:
    id_iter = itertools.count(start=1)

    id: int = field(default_factory=lambda: next(Player.id_iter), init=False)
    mmr: int
    most_played_role: Role

    @classmethod
    def generate_player_pool(cls, size: int) -> list[Player]:
        player_pool: list[Player] = []
        roles = tuple(Role)
        for _ in range(size):
            player = cls(
                mmr=int(random.gauss(1000, 150)),
                most_played_role=random.choice(roles),
            )
            player_pool.append(player)
        return player_pool


@dataclass
class Team:
    players: list[Player]


@dataclass
class Match:
    team1: Team
    team2: Team

    def calculate_fitness_function(self):
        pass
    


if __name__ == "__main__":
    player_pool: list[Player] = Player.generate_player_pool(1000)
    print(player_pool[329])

    team1 = Team(players=player_pool[:5])
    for player in team1.players:
        print(str(player))