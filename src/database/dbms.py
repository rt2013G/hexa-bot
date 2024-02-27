import psycopg
import os
from datetime import datetime
from src.database.model import User, Feedback
from src.utils.config import get_roles

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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS role(
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                );
                """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users_role(
                    user_id INTEGER,
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
                """)
            for role in get_roles():
                cur.execute("""
                INSERT INTO role(name) 
                SELECT %s
                WHERE NOT EXISTS (
                    SELECT *
                    FROM role
                    WHERE name=%s
                )
                """, (role, role))
            conn.commit()
            conn.close()

def insert_user(
        id: int,
        name: str,
        surname: str,
        username: str,
        last_buy_post = datetime(year=2015, month=1, day=15),
        last_sell_post = datetime(year=2015, month=1, day=15)
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
                    last_buy_post,
                    last_sell_post
                ) VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (
                    id,
                    username,
                    name,
                    surname,
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
        
def get_feedbacks(seller_id: int, size = 10) -> list[Feedback]:
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
                feedbacks.append(Feedback(record))
            conn.close()
            return feedbacks

def make_role(user_id: int, role_name: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO users_role(user_id, role_id)
                    SELECT %s, role.id
                    FROM role
                    WHERE role.name=%s;
                """, (user_id, role_name))
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()

def get_role_list(role_name: str) -> list[User]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    SELECT users.id, users.username,
                    users.name, users.surname,
                    users.last_buy_post, users.last_sell_post
                    FROM (users JOIN users_role ON users.id = users_role.user_id)
                        JOIN role ON role.id = users_role.role_id
                    WHERE role.name = %s;
                """, (role_name, ))
            except psycopg.Error as err:
                print(err)
            users = []
            for record in cur.fetchall():
                users.append(User(record))
            conn.close()
            return users

def set_dates_for_user(
        id: int,
        last_buy_post = datetime(year=2015, month=1, day=15),
        last_sell_post = datetime(year=2015, month=1, day=15)
        ) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    UPDATE users
                    SET last_buy_post=%s, last_sell_post=%s
                    WHERE users.id=%s;
                """, (last_buy_post, last_sell_post, id))
            except psycopg.Error as err:
                print(err)
            conn.commit()
            conn.close()
            