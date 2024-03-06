from dotenv import load_dotenv

from src import config as cfg
from src.database import User, update_user_info, update_user_post_dates
from src.database.models.base import create_database, get_connection
from src.database.models.user import insert_user

default_time = cfg.get_default_post_datetime()
mock_users = [
    User((1, None, None, b"test11", default_time, default_time)),
    User((2, b"test2", None, None, default_time, default_time)),
    User((3, b"username", b"test333", None, default_time, default_time)),
    User((4, None, b"test4", b"test44", default_time, default_time)),
]


def start_test_database():
    load_dotenv()
    cfg.GLOBAL_CONFIGS = cfg.load_configs()
    create_database(cfg.get_roles())
    for mock_user in mock_users:
        insert_user(
            mock_user.id,
            mock_user.username,
            mock_user.first_name,
            mock_user.last_name,
        )


def clean_test_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users_role WHERE user_id=1;")
            cur.execute("DELETE FROM users_role WHERE user_id=2;")
            cur.execute("DELETE FROM users_role WHERE user_id=3;")
            cur.execute("DELETE FROM users WHERE id=1;")
            cur.execute("DELETE FROM users WHERE id=2;")
            cur.execute("DELETE FROM users WHERE id=3;")
            cur.execute("DELETE FROM users WHERE id=4;")


def reset_users() -> None:
    for mock_user in mock_users:
        update_user_info(
            mock_user.id,
            mock_user.username,
            mock_user.first_name,
            mock_user.last_name,
        )
        update_user_post_dates(
            mock_user.id,
            cfg.get_default_post_datetime(),
            cfg.get_default_post_datetime(),
        )
