from datetime import datetime

import psycopg

from .base import get_connection


def create_guess_game_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS guess_game(
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP UNIQUE
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users_guess_game(
                    user_id NUMERIC,
                    CONSTRAINT users_guess_game_user_fk
                        FOREIGN KEY(user_id)
                        REFERENCES users(id),
                    game_id INTEGER,
                    CONSTRAINT users_guess_game_game_fk
                        FOREIGN KEY(game_id)
                        REFERENCES guess_game(id),
                    CONSTRAINT users_guess_game_pk
                        PRIMARY KEY (user_id, game_id),
                    user_score INTEGER NOT NULL
                );
                """
            )
            conn.commit()
            conn.close()


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


def insert_user_score(user_id: int, score: int, game_date: datetime) -> None:
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


def get_guess_game_rankings(length: int) -> dict[int, int]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                SELECT users_guess_game.user_id, SUM(users_guess_game.user_score) as score
                FROM users_guess_game
                GROUP BY users_guess_game.user_id
                ORDER BY score DESC
                LIMIT %s;
                """,
                    (length,),
                )
            except psycopg.Error as err:
                print(err)
            scores = {user_id: score for user_id, score in cur.fetchall()}
            conn.close()
            return scores
