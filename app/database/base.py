import os

import psycopg


def get_connection() -> psycopg.Connection:
    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    return psycopg.connect(
        f"""host={host}
        dbname={name}
        user={user}
        password={password}"""
    )
