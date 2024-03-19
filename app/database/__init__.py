from datetime import datetime

from .cache import (
    CACHE,
    RolesEntry,
    get_guess_game_score_from_cache,
    get_id_from_username_cache,
    get_user_from_cache,
    insert_into_guess_game_scores_cache,
    insert_into_roles_cache,
    insert_into_username_cache,
    insert_into_users_cache,
    remove_role_from_roles_cache,
)
from .models import Feedback, MarketPlusPost, Role, User
from .models.role import Role, get_roles_for_user
from .models.user import User
from .role import get_roles, insert_role, remove_role
from .user import (
    get_user_from_id,
    get_user_from_username,
    insert_user,
    update_user_info,
    update_user_last_buy_post,
    update_user_last_sell_post,
)


def create_database() -> None:
    from .feedback import create_feedback_table
    from .guess_game import create_guess_game_table
    from .market_plus_post import create_market_plus_post_table
    from .role import create_role_table
    from .user import create_user_table

    create_user_table()
    create_feedback_table()
    create_role_table()
    create_guess_game_table()
    create_market_plus_post_table()


def insert_guess_game_scores(game_time: datetime, users_scores: dict[int, int]) -> None:
    from .models.guess_game import insert_game, insert_user_score_into_game

    insert_game(game_time)
    for user_id in users_scores.keys():
        score = users_scores[user_id]
        if score > 0:
            insert_user_score_into_game(
                user_id=user_id, score=score, game_date=game_time
            )

    CACHE.cached_guess_game_rankings = {}


def get_top_guess_game_users(length: int) -> dict[int, int]:
    from .models.guess_game import get_guess_game_rankings

    cached_scores = get_guess_game_score_from_cache(length)
    if cached_scores is not None:
        return cached_scores

    rankings = get_guess_game_rankings(length=length)
    insert_into_guess_game_scores_cache(rankings_length=length, users_scores=rankings)
    return rankings
