from dataclasses import dataclass
from datetime import datetime


@dataclass
class GuessGameRankingsEntry:
    rankings: dict[int, int]
    time: datetime


@dataclass
class GamesCache:
    guess_game_rankings: dict[int, GuessGameRankingsEntry]


games_cache = GamesCache(guess_game_rankings={})


def insert_guess_game_rankings(length: int, scores: dict[int, int]) -> None:
    pass


def get_guess_game_rankings(length: int) -> dict[int, int]:
    pass
