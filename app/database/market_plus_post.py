import logging
from datetime import datetime

import psycopg

from app.constants import Dates

from .base import get_connection
from .models import MarketPlusPost


def create_market_plus_post_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                        CREATE TABLE IF NOT EXISTS market_plus_post(
                            message_id NUMERIC PRIMARY KEY,
                            end_date TIMESTAMP NOT NULL,
                            last_posted_date TIMESTAMP NOT NULL,
                            last_posted_market_id NUMERIC,
                            is_deleted BOOLEAN DEFAULT FALSE
                        );
                        """
            )
            conn.commit()
            conn.close()


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
                    (message_id, end_date, Dates.MARKET_EPOCH),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            conn.commit()
            conn.close()


def update_posted_date(message_id: int, market_id: int, date: datetime = None) -> None:
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
                logging.log(logging.ERROR, err)
            conn.commit()
            conn.close()


def update_delete_market_plus_post(message_id: int) -> None:
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
                logging.log(logging.ERROR, err)
            conn.commit()
            conn.close()


def get_posts_to_send() -> list[MarketPlusPost]:
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
                logging.log(logging.ERROR, err)
            posts = [MarketPlusPost(record) for record in cur.fetchall()]
            conn.close()
            return posts


def get_posts_to_delete() -> list[MarketPlusPost]:
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
                logging.log(logging.ERROR, err)
            posts = [MarketPlusPost(record) for record in cur.fetchall()]
            conn.close()
            return posts
