import os

import psycopg


def get_connection() -> psycopg.Connection:
    return psycopg.connect(
        f"""host={os.getenv("DB_HOST")} 
        dbname={os.getenv("DB_NAME")} 
        user={os.getenv("DB_USER")} 
        password={os.getenv("DB_PASSWORD")}"""
    )


def init_db(roles: list[str]) -> None:
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
