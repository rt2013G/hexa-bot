# trunk-ignore-all(ruff)

from .guess_game import get_guess_game_rankings, insert_game, insert_user_score
from .models import Feedback, MarketPlusPost, Role, User
from .role import get_roles, insert_role, remove_role
from .user import (get_user_from_id, get_user_from_username, insert_user,
                   update_user_info, update_user_last_buy_post,
                   update_user_last_sell_post)


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
