import logging
from datetime import datetime

import psycopg

from app.constants import Dates

from .base import get_connection
from .models import User


def create_user_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                    id NUMERIC PRIMARY KEY,
                    username VARCHAR(32),
                    first_name TEXT,
                    last_name TEXT,
                    last_buy_post TIMESTAMP,
                    last_sell_post TIMESTAMP
                );
                """
            )
            conn.commit()
            conn.close()


def insert_user(
    id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    last_buy_post: datetime | None = None,
    last_sell_post: datetime | None = None,
) -> None:
    if last_buy_post is None:
        last_buy_post = Dates.MARKET_EPOCH
    if last_sell_post is None:
        last_sell_post = Dates.MARKET_EPOCH
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
                logging.log(logging.ERROR, err)
            conn.commit()
            conn.close()


def get_user_from_id(id: int) -> User | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT id, username, first_name, last_name, last_buy_post, last_sell_post
                    FROM users
                    WHERE id=%s;
                """,
                    (id,),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            record = cur.fetchone()
            conn.close()
            return User(record) if record else None


def get_user_from_username(username: str) -> User | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT id, username, first_name, last_name, last_buy_post, last_sell_post
                    FROM users
                    WHERE username=%s;
                """,
                    (username,),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            record = cur.fetchone()
            conn.close()
            return User(record) if record else None


def get_all_users() -> list[User]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT id, username, first_name, last_name, last_buy_post, last_sell_post
                    FROM users;
                """
                )
            except psycopg.Error as err:
                print(err)
            users = [User(record) for record in cur.fetchall()]
            conn.close()
            return users


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


def update_user_last_buy_post(
    id: int,
    last_buy_post: datetime,
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE users
                    SET last_buy_post=%s
                    WHERE users.id=%s;
                """,
                    (last_buy_post, id),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def update_user_last_sell_post(
    id: int,
    last_sell_post: datetime,
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE users
                    SET last_sell_post=%s
                    WHERE users.id=%s;
                """,
                    (last_sell_post, id),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()
