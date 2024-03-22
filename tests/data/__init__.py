from dotenv import load_dotenv

from app.constants import Dates
from app.database import User, create_database, insert_user
from app.database.base import get_connection

mock_users = [
    User((1, None, None, b"test11", Dates.MARKET_EPOCH, Dates.MARKET_EPOCH)),
    User((2, b"test2", None, None, Dates.MARKET_EPOCH, Dates.MARKET_EPOCH)),
    User((3, b"username", b"test333", None, Dates.MARKET_EPOCH, Dates.MARKET_EPOCH)),
    User((4, None, b"test4", b"test44", Dates.MARKET_EPOCH, Dates.MARKET_EPOCH)),
]


def create_test_database():
    load_dotenv(override=True)
    create_database()
    for mock_user in mock_users:
        insert_user(
            mock_user.id,
            mock_user.username,
            mock_user.first_name,
            mock_user.last_name,
        )


def clear_test_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users_guess_game WHERE user_id=1;")
            cur.execute("DELETE FROM users_guess_game WHERE user_id=2;")
            cur.execute("DELETE FROM users_guess_game WHERE user_id=3;")
            cur.execute("DELETE FROM users_guess_game WHERE user_id=4;")
            cur.execute("DELETE FROM users_role WHERE user_id=1;")
            cur.execute("DELETE FROM users_role WHERE user_id=2;")
            cur.execute("DELETE FROM users_role WHERE user_id=3;")
            cur.execute("DELETE FROM users WHERE id=1;")
            cur.execute("DELETE FROM users WHERE id=2;")
            cur.execute("DELETE FROM users WHERE id=3;")
            cur.execute("DELETE FROM users WHERE id=4;")
