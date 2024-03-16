from datetime import datetime

import psycopg

from app.config import get_default_post_datetime

from .base import get_connection


class MarketPlusPost:
    def __init__(self, post_data: tuple) -> None:
        self.message_id: int = int(post_data[0])
        self.end_date: datetime = post_data[1]
        self.last_posted_date: datetime = post_data[2]
        self.last_posted_market_id: int | None = (
            int(post_data[3]) if post_data[3] is not None else None
        )


def insert_market_plus_post(message_id: int, end_date: datetime) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                INSERT INTO market_plus_post(
                    message_id,
                    end_date,
                    last_posted_date
                ) VALUES (%s, %s, %s);
                """,
                    (message_id, end_date, get_default_post_datetime()),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def update_market_plus_posted_date(
    message_id: int, market_id: int, date: datetime = None
) -> None:
    if date is None:
        date = datetime.now()
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE market_plus_post
                    SET last_posted_date=%s, last_posted_market_id=%s
                    WHERE market_plus_post.message_id=%s;
                """,
                    (date, market_id, message_id),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def set_delete_market_plus_post(message_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE market_plus_post
                    SET is_deleted=TRUE
                    WHERE market_plus_post.message_id=%s;
                """,
                    (message_id,),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def get_market_plus_posts_to_send() -> list[MarketPlusPost]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT message_id, end_date, last_posted_date, last_posted_market_id
                    FROM market_plus_post
                    WHERE end_date > CURRENT_TIMESTAMP
                    AND DATE(last_posted_date) < DATE(CURRENT_TIMESTAMP);
                """
                )
            except psycopg.Error as err:
                print(err)
            records = cur.fetchall()
            posts = [MarketPlusPost(record) for record in records]
            conn.close()
            return posts


def get_market_plus_posts_to_delete() -> list[MarketPlusPost]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT message_id, end_date, last_posted_date, last_posted_market_id
                    FROM market_plus_post
                    WHERE end_date < CURRENT_TIMESTAMP
                    AND is_deleted = FALSE;
                """
                )
            except psycopg.Error as err:
                print(err)
            records = cur.fetchall()
            posts = [MarketPlusPost(record) for record in records]
            conn.close()
            return posts
