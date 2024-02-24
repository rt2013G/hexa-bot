import psycopg
import os
from datetime import datetime
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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback(
                    id SERIAL PRIMARY KEY,
                    seller_id INTEGER,
                    CONSTRAINT seller_fk
                        FOREIGN KEY(seller_id)
                        REFERENCES users(id),
                    buyer_id INTEGER,
                    CONSTRAINT buyer_fk
                        FOREIGN KEY(buyer_id)
                        REFERENCES users(id),
                    CONSTRAINT seller_is_not_buyer 
                        CHECK(seller_id != buyer_id),
                    contents TEXT,
                    date TIMESTAMP
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

def insert_feedback(
        seller_id: int,
        buyer_id: int,
        contents: str,
        date = datetime.now()
        ) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                INSERT INTO feedback(
                    seller_id,
                    buyer_id,
                    contents,
                    date
                ) VALUES (%s, %s, %s, %s);
                """,
                (
                    seller_id,
                    buyer_id,
                    contents,
                    date
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
        
def get_users(size = 10) -> list[User]:
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
        
def get_feedbacks(seller_id: int, size = 10) -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    SELECT *
                    FROM feedback
                    WHERE seller_id=%s;
                """, (seller_id, ))
            except psycopg.Error as err:
                print(err)
            records = cur.fetchmany(size)
            feedbacks = []
            for record in records:
                feedbacks.append(record)
            conn.close()
            return feedbacks