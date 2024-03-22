import logging

import psycopg

from app.constants import Roles

from .base import get_connection
from .models import Role


def create_role_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
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
            roles = {
                Roles.ADMIN,
                Roles.SELLER,
                Roles.SCAMMER,
                Roles.JUDGE,
                Roles.MODERATOR,
            }
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


def insert_role(user_id: int, role_name: Role) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO users_role(user_id, role_id)
                    SELECT %s, role.id
                    FROM role
                    WHERE role.name=%s;
                """,
                    (user_id, role_name),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            conn.commit()
            conn.close()


def remove_role(user_id: int, role_name: Role) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    DELETE FROM users_role
                    WHERE users_role.user_id = %s
                    AND users_role.role_id = (
                        SELECT role.id
                        FROM role
                        WHERE role.name=%s
                    );
                """,
                    (user_id, role_name),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            conn.commit()
            conn.close()


def get_roles(user_id: int) -> set[Role]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT role.name
                    FROM (users JOIN users_role ON users.id = users_role.user_id)
                        JOIN role ON role.id = users_role.role_id
                    WHERE users.id = %s;
                """,
                    (user_id,),
                )
            except psycopg.Error as err:
                logging.log(logging.ERROR, err)
            roles = set()
            for record in cur.fetchall():
                value: str = record[0]
                try:
                    value = record[0].decode("utf-8")
                except AttributeError:
                    pass
                roles.add(value)
            conn.close()
            return roles
