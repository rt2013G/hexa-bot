from datetime import datetime

from src import cache as c
from src.config import get_bot_username, get_max_username_length, get_roles
from src.database.dbms import get_role_list, get_user_from_id, get_user_from_username
from src.database.model import User


def get_user_from_message_command(message_text: str, command_text: str) -> User | None:
    msg = clean_command_text(message_text, command_text)
    if len(msg) > 1 + get_max_username_length():
        return None

    if "@" in msg:
        msg = msg.replace("@", "")
        if msg.isnumeric():
            return None
        else:
            return get_user_from_username(username=msg)
    elif msg.isnumeric():
        return get_user_from_id(int(msg))

    return None


def get_user_from_text(message_text: str) -> User | None:
    if "@" not in message_text:
        return None

    for word in message_text.split():
        if "@" in word:
            username = word.replace("@", "")
            if len(username) > 0:
                return get_user_from_username(username=username)

    return None


def is_role(user_id: int, role_name: str) -> bool:
    if role_name not in get_roles():
        return False
    if role_name == "admin":
        if user_id in c.ADMIN_CACHE:
            return True
    if role_name == "seller":
        user_entry: c.UserCacheEntry | None = c.USERS_CACHE.get(user_id)
        if user_entry is not None:
            return user_entry.is_seller

    for user in get_role_list(role_name):
        if user.id == user_id:
            if role_name == "admin" and user_id not in c.ADMIN_CACHE:
                c.ADMIN_CACHE.append(user_id)
            elif role_name == "seller":
                c.insert_into_cache(user, True, datetime.now())
            return True

    return False


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
    user = get_user_from_id(user_id)
    if user is None:
        return False

    return True if user.last_sell_post.date() == datetime.today().date() else False


def has_sent_buy_post_today(user_id: int) -> bool:
    user = get_user_from_id(user_id)
    if user is None:
        return False

    return True if user.last_buy_post.date() == datetime.today().date() else False
