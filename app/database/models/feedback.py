from datetime import datetime

import psycopg

from .base import get_connection


class Feedback:
    def __init__(self, feedback_data: tuple) -> None:
        self.id: int = feedback_data[0]
        self.seller_id: int = feedback_data[1]
        self.buyer_id: int = feedback_data[2]
        try:
            self.contents: str = feedback_data[3].decode("utf-8")
        except AttributeError:
            self.contents: str = feedback_data[3]
        self.date: datetime = feedback_data[4]


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
                print(err)
            conn.commit()
            conn.close()


def get_feedbacks(seller_id: int, size=10) -> list[Feedback]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT *
                    FROM feedback
                    WHERE seller_id=%s;
                """,
                    (seller_id,),
                )
            except psycopg.Error as err:
                print(err)
            records = cur.fetchmany(size)
            feedbacks = []
            for record in records:
                feedbacks.append(Feedback(record))
            conn.close()
            return feedbacks
