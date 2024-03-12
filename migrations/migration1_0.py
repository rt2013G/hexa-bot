import json
import os
from datetime import datetime

from app.constants import Roles
from app.database.models.base import create_database
from app.database.models.feedback import insert_feedback
from app.database.models.role import make_role
from app.database.models.user import (
    get_user_from_id,
    get_user_from_username,
    insert_user,
)


def upgrade() -> None:
    migrate_users()
    migrate_feedbacks()


def migrate_users() -> None:
    create_database()
    path = "migrations/data/users.json"
    data: list[dict]
    i = 0
    with open(os.path.abspath(path), "r") as f:
        data = list(json.load(f))
    for user in data:
        username = user["tag"].replace("@", "")
        if username == "None":
            username = None
        print(f"inserting user:{i}, {username}")
        insert_user(
            id=int(user["id"]),
            username=username,
            first_name=user["name"],
            last_buy_post=user["last_buy_post"],
            last_sell_post=user["last_sell_post"],
        )
        if user["is_seller"]:
            make_role(user_id=user["id"], role_name=Roles.SELLER)
        i += 1


def migrate_feedbacks() -> None:
    path = "migrations/data/feedback.json"
    data: list[dict]
    with open(os.path.abspath(path), "r") as f:
        data = list(json.load(f))

    i = 0
    for feed in data:
        buyer_id = feed["buyer"]
        buyer = get_user_from_id(buyer_id)
        if buyer is None:
            continue

        sellers = feed["seller"].split("@")[1:]
        contents = feed["text"]
        date = datetime.fromisoformat(feed["date"])
        for seller_username in sellers:
            if seller_username == "admin":
                continue
            seller = get_user_from_username(seller_username)
            if seller is None:
                continue
            if seller.id == buyer.id:
                continue
            print(
                f"inserting feedback: {i}, feedback: {seller.username}, {buyer.username}, {date}"
            )
            insert_feedback(
                seller_id=seller.id, buyer_id=buyer_id, contents=contents, date=date
            )

            i += 1
