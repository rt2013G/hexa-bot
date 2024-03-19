import logging
from datetime import datetime

import psycopg

from .base import get_connection
from .models import Feedback


def create_feedback_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                        CREATE TABLE IF NOT EXISTS feedback(
                            id SERIAL PRIMARY KEY,
                            seller_id NUMERIC,
                            CONSTRAINT seller_fk
                                FOREIGN KEY(seller_id)
                                REFERENCES users(id),
                            buyer_id NUMERIC,
                            CONSTRAINT buyer_fk
                                FOREIGN KEY(buyer_id)
                                REFERENCES users(id),
                            CONSTRAINT seller_is_not_buyer 
                                CHECK(seller_id != buyer_id),
                            contents TEXT NOT NULL,
                            date TIMESTAMP
                        );
                        """
            )


def insert_feedback(
    seller_id: int, buyer_id: int, contents: str, date: datetime
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                INSERT INTO feedback(
                    seller_id,
                    buyer_id,
                    contents,
                    date
                ) VALUES (%s, %s, %s, %s);
                """,
                    (seller_id, buyer_id, contents, date),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            conn.commit()
            conn.close()


def get_feedbacks(seller_id: int) -> list[Feedback]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT id, seller_id, buyer_id, contents, date
                    FROM feedback
                    WHERE seller_id=%s;
                """,
                    (seller_id,),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            feedbacks = [Feedback(record) for record in cur.fetchall()]
            conn.close()
            return feedbacks
