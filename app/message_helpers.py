import re

from app.cache import get_user
from app.constants import MessageLimits
from app.database import User


def get_user_from_command_arg(arg: str) -> User | None:
    if len(arg) > MessageLimits.MAX_USERNAME_LENGTH + 1:
        return None

    arg = arg.replace("@", "")
    if arg.isnumeric():
        return get_user(id=int(arg))
    else:
        return get_user(username=arg)


def get_user_from_text(message_text: str) -> User | None:
    if "@" not in message_text:
        return None

    for word in message_text.split():
        if "@" in word:
            username = remove_non_alpha_characters(word)
            if len(username) > 0:
                if user := get_user(username=username):
                    return user

    return None


def remove_non_alpha_characters(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", text)
