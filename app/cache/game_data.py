from dataclasses import dataclass
from datetime import datetime

from app import database as db


@dataclass
class GuessGameRankingsEntry:
    rankings: dict[int, int]
    time: datetime


@dataclass
class GamesCache:
    guess_game_rankings: dict[int, GuessGameRankingsEntry]


games_cache = GamesCache(guess_game_rankings={})


def insert_guess_game_scores(game_time: datetime, scores: dict[int, int]) -> None:
    db.insert_game(date=game_time)
    for user_id, score in scores.items():
        if score > 0:
            db.insert_user_score(user_id=user_id, score=score, game_date=game_time)
    games_cache.guess_game_rankings = {}


def get_guess_game_rankings(length: int) -> dict[int, int]:
    if rankings_entry := games_cache.guess_game_rankings.get(length):
        return rankings_entry.rankings

    rankings = db.get_guess_game_rankings(length=length)
    games_cache.guess_game_rankings[length] = GuessGameRankingsEntry(
        rankings=rankings, time=datetime.now()
    )
    return rankings
