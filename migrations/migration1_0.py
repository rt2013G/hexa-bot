import json
import os

from app.constants import Roles
from app.database.models.base import create_database
from app.database.models.role import make_role
from app.database.models.user import insert_user


def upgrade() -> None:
    create_database()
    path = "migrations/data/users.json"
    data: list[dict]
    i = 0
    with open(os.path.abspath(path), "r") as f:
        data = list(json.load(f))
    for user in data:
        if user["tag"] == "@None":
            user["tag"] = None
        insert_user(
            id=int(user["id"]),
            username=user["tag"],
            first_name=user["name"],
            last_buy_post=user["last_buy_post"],
            last_sell_post=user["last_sell_post"],
        )
        if user["is_seller"]:
            make_role(user_id=user["id"], role_name=Roles.SELLER)
        print(f"inserting user:{i}")
        i += 1
