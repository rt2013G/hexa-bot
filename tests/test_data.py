from dataclasses import dataclass

from dotenv import load_dotenv

from src import config as cfg
from src.database import User, update_user_info, update_user_post_dates
from src.database.models.base import create_database, get_connection
from src.database.models.user import insert_user


@dataclass
class MockUser:
    id: int
    username: str | None
    first_name: str | None
    last_name: str | None


mock_data = [
    MockUser(1, None, None, "test11"),
    MockUser(2, "test2", None, None),
    MockUser(3, "username", "test333", None),
    MockUser(4, None, "test4", "test44"),
]


def start_test_database():
    load_dotenv()
    cfg.GLOBAL_CONFIGS = cfg.load_configs()
    create_database(cfg.get_roles())
    for mock_user in mock_data:
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
    for mock_user in mock_data:
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


def compare_mock_to_user(mock: MockUser, user: User) -> bool:
    return (
        mock.id == user.id
        and mock.username == user.username
        and mock.first_name == user.first_name
        and mock.last_name == user.last_name
    )
