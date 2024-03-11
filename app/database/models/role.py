from typing import Literal

import psycopg

from .base import get_connection
from .user import User

type Role = Literal["admin", "seller", "scammer", "judge"]

def make_role(user_id: int, role_name: Role) -> None:
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
                print(err)
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
                print(err)
            conn.commit()
            conn.close()


def get_role_list(role_name: Role) -> list[User]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT users.id, users.username,
                    users.first_name, users.last_name,
                    users.last_buy_post, users.last_sell_post
                    FROM (users JOIN users_role ON users.id = users_role.user_id)
                        JOIN role ON role.id = users_role.role_id
                    WHERE role.name = %s;
                """,
                    (role_name,),
                )
            except psycopg.Error as err:
                print(err)
            users = []
            for record in cur.fetchall():
                users.append(User(record))
            conn.close()
            return users


def get_roles_for_user(user_id: int) -> list[Role]:
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
                print(err)
            roles = []
            for record in cur.fetchall():
                value: str = record[0]
                try:
                    value = record[0].decode("utf-8")
                except AttributeError:
                    pass
                roles.append(value)
            conn.close()
            return roles