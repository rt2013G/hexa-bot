import psycopg

from src.database import cache as c

from .base import get_connection
from .user import User


def make_role(user_id: int, role_name: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO users_role(user_id, role_id)
                    SELECT %s, role.id
                    FROM role
                    WHERE role.name=%s;
                """,
                    (user_id, role_name),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()
    if role_name == "seller" and user_id in c.USERS_CACHE.keys():
        c.USERS_CACHE[user_id].is_seller = True


def remove_role(user_id: int, role_name: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    DELETE FROM users_role
                    WHERE users_role.user_id = %s
                    AND users_role.role_id = (
                        SELECT role.id
                        FROM role
                        WHERE role.name=%s
                    );
                """,
                    (user_id, role_name),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()
    if role_name == "admin" and user_id in c.ADMIN_CACHE:
        c.ADMIN_CACHE.remove(user_id)
    elif role_name == "seller" and user_id in c.USERS_CACHE.keys():
        c.USERS_CACHE[user_id].is_seller = False


def get_role_list(role_name: str) -> list[User]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT users.id, users.username,
                    users.first_name, users.last_name,
                    users.last_buy_post, users.last_sell_post
                    FROM (users JOIN users_role ON users.id = users_role.user_id)
                        JOIN role ON role.id = users_role.role_id
                    WHERE role.name = %s;
                """,
                    (role_name,),
                )
            except psycopg.Error as err:
                print(err)
            users = []
            for record in cur.fetchall():
                users.append(User(record))
            conn.close()
            return users
