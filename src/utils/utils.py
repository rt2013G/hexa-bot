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
    return text.replace(get_bot_username(), "").replace(command, "").replace(" ", "")
