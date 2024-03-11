import os

import psycopg

from app.constants import Roles


def get_connection(
    host: str | None = None,
    name: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> psycopg.Connection:
    if host is None:
        host = os.getenv("DB_HOST")
    if name is None:
        name = os.getenv("DB_NAME")
    if user is None:
        user = os.getenv("DB_USER")
    if password is None:
        password = os.getenv("DB_PASSWORD")
    return psycopg.connect(
        f"""host={host}
        dbname={name}
        user={user}
        password={password}"""
    )


def create_database() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                    id NUMERIC PRIMARY KEY,
                    username VARCHAR(32) UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    last_buy_post TIMESTAMP,
                    last_sell_post TIMESTAMP
                );
                """
            )
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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS role(
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users_role(
                    user_id NUMERIC,
                    CONSTRAINT user_fk
                        FOREIGN KEY(user_id)
                        REFERENCES users(id),
                    role_id INTEGER,
                    CONSTRAINT role_fk
                        FOREIGN KEY(role_id)
                        REFERENCES role(id),
                    CONSTRAINT users_role_pk
                        PRIMARY KEY (user_id, role_id)
                );
                """
            )
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
            roles = {Roles.ADMIN, Roles.SELLER, Roles.SCAMMER, Roles.JUDGE}
            for role in roles:
                cur.execute(
                    """
                INSERT INTO role(name) 
                SELECT %s
                WHERE NOT EXISTS (
                    SELECT *
                    FROM role
                    WHERE name=%s
                )
                """,
                    (role, role),
                )
            conn.commit()
            conn.close()
