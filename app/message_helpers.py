import re
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
