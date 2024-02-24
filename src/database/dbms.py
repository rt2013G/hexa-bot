import psycopg
import os
from src.database.model import User

def get_connection() -> psycopg.Connection:
    return psycopg.connect(
        f"""host={os.getenv("DB_HOST")} 
        dbname={os.getenv("DB_NAME")} 
        user={os.getenv("DB_USER")} 
        password={os.getenv("DB_PASSWORD")}"""
        )

def init_db() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(32) UNIQUE,
                    name TEXT,
                    surname TEXT,
                    is_seller BOOLEAN,
                    last_buy_post TIMESTAMP,
                    last_sell_post TIMESTAMP
                );
                """)
            conn.commit()
            conn.close()

def insert_user(
        id: int,
        name: str,
        surname: str,
        username: str,
        is_seller = False,
        last_buy_post = "2015-01-15",
        last_sell_post = "2015-01-15"
        ) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                INSERT INTO users(
                    id,
                    username,
                    name,
                    surname,
                    is_seller,
                    last_buy_post,
                    last_sell_post
                ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    id,
                    username,
                    name,
                    surname,
                    is_seller,
                    last_buy_post,
                    last_sell_post
                ))
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()

def get_user_from_id(id: int) -> User:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    SELECT *
                    FROM users
                    WHERE id=%s;
                """, (id, ))
            except psycopg.Error as err:
                print(err)
            record = cur.fetchone()
            conn.close()
            return User(record)
        
def get_users(size: int) -> list[User]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    SELECT *
                    FROM users;
                """)
            except psycopg.Error as err:
                print(err)
            records = cur.fetchmany(size)
            users = []
            for record in records:
                users.append(User(record))
            conn.close()
            return users