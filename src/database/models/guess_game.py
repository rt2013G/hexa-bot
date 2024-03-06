from datetime import datetime

import psycopg

from .base import get_connection


def insert_game(date: datetime) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                INSERT INTO guess_game(
                    date
                ) VALUES (%s);
                """,
                    (date,),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def insert_user_score_into_game(user_id: int, score: int, game_date: datetime) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                INSERT INTO users_guess_game(user_id, game_id, user_score)
                    SELECT %s, guess_game.id, %s
                    FROM guess_game
                    WHERE guess_game.date=%s;
                """,
                    (user_id, score, game_date),
                )
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()


def get_total_score_for_user(user_id: int) -> int | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                SELECT SUM(users_guess_game.user_score)
                FROM users_guess_game
                WHERE users_guess_game.user_id = %s;
                """,
                    (user_id,),
                )
            except psycopg.Error as err:
                print(err)
            record = cur.fetchone()
            conn.close()
            if record is not None:
                return record[0]
