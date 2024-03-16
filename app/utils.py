import json
import os
import random
import re
from datetime import datetime

import requests

from app.config import get_bot_username
from app.database import User, get_user


def get_user_from_message_command(message_text: str, command_text: str) -> User | None:
    msg = clean_command_text(message_text, command_text)
    MAX_USERNAME_LENGTH = 32
    if len(msg) > 1 + MAX_USERNAME_LENGTH:
        return None

    if "@" in msg:
        msg = msg.replace("@", "")
        if msg.isnumeric():
            return None
        else:
            return get_user(username=msg)
    elif msg.isnumeric():
        return get_user(id=int(msg))

    return None


def get_user_from_text(message_text: str) -> User | None:
    if "@" not in message_text:
        return None

    for word in message_text.split():
        if "@" in word:
            username = re.sub(r"[^a-zA-Z0-9_]", "", word)
            if len(username) > 0:
                user = get_user(username=username)
                if user is not None:
                    return user

    return None


def clean_command_text(text: str, command: str) -> str:
    return text.replace(get_bot_username(), "").replace(command, "").lstrip()


def get_auth_code_from_id(user_id: int) -> int:
    return int(str(user_id**2)[0:6])


def is_sell_post(text: str) -> bool:
    text = text.lower()
    return (
        True
        if "vendo" in text
        or "vendere" in text
        or "vendesi" in text
        or "vendono" in text
        or "ammortizzo" in text
        or "up" == text
        else False
    )


def is_buy_post(text: str) -> bool:
    text = text.lower()
    return (
        True
        if "cerco" in text
        or "compro" in text
        or "cercare" in text
        or "cercasi" in text
        or "cercano" in text
        else False
    )


def is_feedback_post(text: str) -> bool:
    text = text.lower()
    return (
        True
        if "feedback" in text
        or "feed" in text
        or "feedb" in text
        or "feed" in text in text
        else False
    )


def has_sent_sell_post_today(user_id: int) -> bool:
    user = get_user(id=user_id)
    if user is None:
        return False

    return True if user.last_sell_post.date() == datetime.today().date() else False


def has_sent_buy_post_today(user_id: int) -> bool:
    user = get_user(id=user_id)
    if user is None:
        return False

    return True if user.last_buy_post.date() == datetime.today().date() else False


def load_card_name_db() -> None:
    path = "app/static/card_names.json"
    if not os.path.exists(os.path.abspath(path)):
        CARD_NAME_URL = "https://db.ygorganization.com/data/idx/card/name/en"
        response = requests.get(CARD_NAME_URL, timeout=10)
        response_json = json.loads(response.content)
        with open(os.path.abspath(path), "w") as f:
            json.dump(response_json, f)


def get_random_card_name() -> str:
    path = "app/static/card_names.json"
    card_database: dict[str, list[int]]
    with open(os.path.abspath(path), "r") as f:
        card_database = dict(json.load(f))

    # trunk-ignore(bandit/B311)
    return random.choice(list(card_database.keys()))


def get_rankings_message_from_scores(users_scores: dict[int, int]) -> str:
    scores: list[tuple[str, int]] = []
    for key in sorted(
        users_scores,
        key=users_scores.get,
        reverse=True,
    ):
        value = users_scores[key]
        user = get_user(key)
        user_to_display = ""
        if user.username:
            user_to_display = "@" + user.username
        else:
            if user.first_name and user.last_name:
                user_to_display = user.first_name + user.last_name
            elif user.first_name:
                user_to_display = user.first_name
            elif user.last_name:
                user_to_display = user.last_name

        scores.append((user_to_display, value))

    emoji_dict = {0: "🥇", 1: "🥈", 2: "🥉"}
    rankings = ""
    for i, score in enumerate(scores):
        emoji_to_add = emoji_dict.get(i)
        if emoji_to_add is None:
            emoji_to_add = ""

        rankings += f"{emoji_to_add} {score[0]}, punteggio: {score[1]}\n"

    return rankings
