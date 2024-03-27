import re
from datetime import datetime
from typing import Literal

from telegram import Message, ReplyKeyboardRemove
from telegram.error import BadRequest, Forbidden, TimedOut
from telegram.ext import ContextTypes
from telegram.helpers import effective_message_type

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


async def send_message_with_bot(
    recipient_id: int, message_to_send: Message, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message_type: Literal["text", "photo", "video", "document"] = (
        effective_message_type(message_to_send)
    )
    match message_type:
        case "text":
            try:
                await context.bot.send_message(
                    chat_id=recipient_id,
                    text=message_to_send.text,
                    reply_markup=ReplyKeyboardRemove(),
                )
            except (TimedOut, Forbidden, BadRequest) as err:
                raise err
        case "photo":
            try:
                await context.bot.send_photo(
                    chat_id=recipient_id,
                    photo=message_to_send.photo[0],
                    caption=message_to_send.caption,
                    reply_markup=ReplyKeyboardRemove(),
                )
            except (TimedOut, Forbidden, BadRequest) as err:
                raise err
        case "video":
            try:
                await context.bot.send_video(
                    chat_id=recipient_id,
                    video=message_to_send.video,
                    caption=message_to_send.caption,
                    reply_markup=ReplyKeyboardRemove(),
                )
            except (TimedOut, Forbidden, BadRequest) as err:
                raise err
        case "document":
            try:
                await context.bot.send_document(
                    chat_id=recipient_id,
                    document=message_to_send.document,
                    caption=message_to_send.caption,
                    reply_markup=ReplyKeyboardRemove(),
                )
            except (TimedOut, Forbidden, BadRequest) as err:
                raise err
        case _:
            raise Forbidden


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


def is_sell_post(text: str) -> bool:
    text = text.lower()
    if text == "up":
        return True
    keywords = [
        "vendo",
        "vendere",
        "vendesi",
        "vendono,",
        "ammortizzo",
        "ammortizzare",
        "scambio",
        "scambiare",
    ]
    return True if any(word in text for word in keywords) else False


def is_buy_post(text: str) -> bool:
    text = text.lower()
    keywords = ["cerco", "compro", "cercare", "cercasi", "cercano"]
    return True if any(word in text for word in keywords) else False


def is_feedback_post(text: str) -> bool:
    text = text.lower()
    keywords = ["feedback", "feed", "feedb"]
    return True if any(word in text for word in keywords) else False


def has_sent_buy_post_today(user: User) -> bool:
    return True if user.last_buy_post.date() == datetime.today().date() else False


def has_sent_sell_post_today(user: User) -> bool:
    return True if user.last_sell_post.date() == datetime.today().date() else False
