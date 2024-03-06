import json
import os
import random
from datetime import datetime

from src.config import get_bot_username, get_max_username_length
from src.database import User, get_user


def get_user_from_message_command(message_text: str, command_text: str) -> User | None:
    msg = clean_command_text(message_text, command_text)
    if len(msg) > 1 + get_max_username_length():
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
            username = word.replace("@", "")
            if len(username) > 0:
                return get_user(username=username)

    return None


def clean_command_text(text: str, command: str) -> str:
    return text.replace(get_bot_username(), "").replace(command, "").lstrip()


def get_auth_code_from_id(user_id: int) -> int:
    return int(str(user_id**2)[0:6])


def is_sell_post(text: str) -> bool:
    text = text.lower()
    return (
        True
        if "#vendo" in text
        or "vendo" in text
        or "vendere" in text
        or "vendesi" in text
        or "vendono" in text
        or "ammortizzo" in text
        else False
    )


def is_buy_post(text: str) -> bool:
    text = text.lower()
    return (
        True
        if "#cerco" in text
        or "cerco" in text
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
        if "#feedback" in text
        or "feedback" in text
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


def get_random_card_name() -> str:
    path = "configs/card_names.json"
    card_database: dict[str, list[int]]
    with open(os.path.abspath(path)) as f:
        card_database = dict(json.load(f))

    # trunk-ignore(bandit/B311)
    return random.choice(list(card_database.keys()))
