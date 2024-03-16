from datetime import datetime

import psycopg

from app.config import get_default_post_datetime

from .base import get_connection


class MarketPlusPost:
    def __init__(self, post_data: tuple) -> None:
        self.message_id: int = post_data[0]
        self.end_date: datetime = post_data[1]
        self.last_posted_date: datetime = post_data[2]


def insert_market_plus_post(message_id: int, end_date: int) -> None:
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


def update_market_plus_posted_date(message_id: int, date: datetime = None) -> None:
    if date is None:
        date = datetime.now()
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE market_plus_post
                    SET last_posted_date=%s
                    WHERE market_plus_post.message_id=%s;
                """,
                    (date, message_id),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def get_active_market_plus_posts() -> list[MarketPlusPost]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT message_id, end_date, last_posted_date
                    FROM market_plus_post
                    WHERE end_date > CURRENT_TIMESTAMP;
                """
                )
            except psycopg.Error as err:
                print(err)
            records = cur.fetchall()
            posts = [MarketPlusPost(record) for record in records]
            conn.close()
            return posts
