from datetime import datetime

import psycopg

from src.database import cache as c

from .base import get_connection


class User:
    def __init__(self, user_data: tuple) -> None:
        self.id: int = int(user_data[0])
        self.username: str | None = (
            None if user_data[1] is None else user_data[1].decode("utf-8")
        )
        self.first_name: str | None = (
            None if user_data[2] is None else user_data[2].decode("utf-8")
        )
        self.last_name: str | None = (
            None if user_data[3] is None else user_data[3].decode("utf-8")
        )
        self.last_buy_post: datetime = user_data[4]
        self.last_sell_post: datetime = user_data[5]


def insert_user(
    id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    last_buy_post: datetime = datetime(year=2015, month=1, day=15),
    last_sell_post: datetime = datetime(year=2015, month=1, day=15),
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                INSERT INTO users(
                    id,
                    username,
                    first_name,
                    last_name,
                    last_buy_post,
                    last_sell_post
                ) VALUES (%s, %s, %s, %s, %s, %s);
                """,
                    (
                        id,
                        username,
                        first_name,
                        last_name,
                        last_buy_post,
                        last_sell_post,
                    ),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def get_user_from_id(id: int) -> User | None:
    user_entry: c.UserCacheEntry | None = c.USERS_CACHE.get(id)
    if user_entry is not None:
        return user_entry.user
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE id=%s;
                """,
                    (id,),
                )
            except psycopg.Error as err:
                print(err)
            record = cur.fetchone()
            conn.close()
            if record is None:
                return None
            return User(record)


def get_user_from_username(username: str) -> User | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE username=%s;
                """,
                    (username,),
                )
            except psycopg.Error as err:
                print(err)
            record = cur.fetchone()
            conn.close()
            if record is None:
                return None
            return User(record)


def get_users(size=1000000) -> list[User]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT *
                    FROM users;
                """
                )
            except psycopg.Error as err:
                print(err)
            records = cur.fetchmany(size)
            users = []
            for record in records:
                users.append(User(record))
            conn.close()
            return users


def update_user_dates(
    id: int,
    last_buy_post=datetime(year=2015, month=1, day=15),
    last_sell_post=datetime(year=2015, month=1, day=15),
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE users
                    SET last_buy_post=%s, last_sell_post=%s
                    WHERE users.id=%s;
                """,
                    (last_buy_post, last_sell_post, id),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()
    if id in c.USERS_CACHE.keys():
        del c.USERS_CACHE[id]


def update_user_info(
    id: int, username: str | None, first_name: str | None, last_name: str | None
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE users
                    SET username=%s, first_name=%s, last_name=%s
                    WHERE users.id=%s;
                """,
                    (username, first_name, last_name, id),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()
    if id in c.USERS_CACHE.keys():
        del c.USERS_CACHE[id]