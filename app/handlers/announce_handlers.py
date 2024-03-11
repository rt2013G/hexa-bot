from dataclasses import dataclass
from typing import Literal

from telegram import Message, ReplyKeyboardRemove, Update
from telegram.error import BadRequest, Forbidden, TimedOut
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import effective_message_type

from app.database.models.user import get_users
from app.filters import AdminFilter, DebugUserFilter
from app.logger import with_logging
from app.utils import get_user_from_message_command


def get_announce_handlers() -> list:
    return [
        CommandHandler("announce", announce_handler, DebugUserFilter()),
        CommandHandler("sendmessageto", send_private_message_handler, AdminFilter()),
    ]


@dataclass
class AnnounceData:
    users_id_list: list[int]
    message: Message


@with_logging
async def announce_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    if (
        update.message.reply_to_message is None
        or update.message.reply_to_message.from_user.id != update.message.from_user.id
    ):
        await context.bot.send_message(
            update.message.from_user.id,
            "Per inviare un annuncio, scrivi prima il messaggio, dopodiché rispondi ad esso con /announce.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await context.bot.send_message(
        update.message.from_user.id,
        "Inizio ad inviare i messaggi, potrebbe volerci del tempo...",
        reply_markup=ReplyKeyboardRemove(),
    )

    message = update.message.reply_to_message
    users = get_users()
    users_id_list: list[int] = []
    for user in users:
        users_id_list.append(user.id)
    context.job_queue.run_repeating(
        callback=send_announce_job,
        interval=10,
        first=1,
        data=AnnounceData(users_id_list=users_id_list, message=message),
        name=f"announce{message.id}",
    )


@with_logging
async def send_private_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return

    if (
        update.message.reply_to_message is None
        or update.message.reply_to_message.from_user.id != update.message.from_user.id
    ):
        await context.bot.send_message(
            update.message.from_user.id,
            "Per inviare un messaggio tramite bot, scrivi prima il messaggio, dopodiché rispondi ad esso con /sendmessageto @username.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    user_to_dm = get_user_from_message_command(update.message.text, "/sendmessageto")
    if user_to_dm is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return

    await send_message_with_bot(
        recipient_id=user_to_dm.id,
        message_to_send=update.message.reply_to_message,
        context=context,
    )

    await context.bot.send_message(
        update.message.from_user.id,
        "Messaggio inviato!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def send_message_with_bot(
    recipient_id: int, message_to_send: Message, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message_type: Literal["text", "photo", "video", "document"] = (
        effective_message_type(message_to_send)
    )
    if message_type == "text":
        try:
            await context.bot.send_message(
                chat_id=recipient_id,
                text=message_to_send.text,
                reply_markup=ReplyKeyboardRemove(),
            )
        except (TimedOut, Forbidden, BadRequest) as err:
            raise err
    elif message_type == "photo":
        try:
            await context.bot.send_photo(
                chat_id=recipient_id,
                photo=message_to_send.photo[0],
                caption=message_to_send.caption,
                reply_markup=ReplyKeyboardRemove(),
            )
        except (TimedOut, Forbidden, BadRequest) as err:
            raise err
    elif message_type == "video":
        try:
            await context.bot.send_video(
                chat_id=recipient_id,
                video=message_to_send.video,
                caption=message_to_send.caption,
                reply_markup=ReplyKeyboardRemove(),
            )
        except (TimedOut, Forbidden, BadRequest) as err:
            raise err
    elif message_type == "document":
        try:
            await context.bot.send_document(
                chat_id=recipient_id,
                document=message_to_send.document,
                caption=message_to_send.caption,
                reply_markup=ReplyKeyboardRemove(),
            )
        except (TimedOut, Forbidden, BadRequest) as err:
            raise err
    else:
        raise Forbidden


async def send_announce_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    announce_data: AnnounceData = job.data
    users_id_list: list[int] = list(announce_data.users_id_list)
    for user_id in users_id_list:
        timed_out = False
        try:
            await send_message_with_bot(
                recipient_id=user_id,
                message_to_send=announce_data.message,
                context=context,
            )
        except TimedOut:
            timed_out = True
        except (Forbidden, BadRequest):
            pass

        if timed_out:
            return
        else:
            announce_data.users_id_list.remove(user_id)

    if len(announce_data.users_id_list) == 0:
        job.schedule_removal()
