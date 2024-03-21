import sys
from dataclasses import dataclass

from telegram import Message, ReplyKeyboardRemove, Update
from telegram.error import BadRequest, Forbidden, TimedOut
from telegram.ext import CommandHandler, ContextTypes, filters

from app.constants import Messages
from app.database import get_all_users
from app.filters import AdminFilter, DebugUserFilter
from app.message_helpers import (get_user_from_command_arg,
                                 send_message_with_bot)


def helpers_handlers() -> list[CommandHandler]:
    return [
        CommandHandler("info", user_info_handler, AdminFilter()),
        CommandHandler(
            "shutdown", shutdown_handler, DebugUserFilter() & filters.ChatType.PRIVATE
        ),
        CommandHandler("message", send_private_message_handler, AdminFilter()),
        CommandHandler("announce", announce_handler, DebugUserFilter()),
    ]


async def user_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        return

    if user := get_user_from_command_arg(arg=context.args[0]):
        await update.message.reply_text(
            f"Utente: {user.first_name} {user.last_name}.\nUsername: @{user.username}\nId: {user.id}",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )


async def shutdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Shutting down...", reply_markup=ReplyKeyboardRemove()
    )
    await context.application.stop()
    sys.exit(0)


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
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return

    await send_message_with_bot(
        recipient_id=user.id,
        message_to_send=update.message.reply_to_message,
        context=context,
    )
    await context.bot.send_message(
        update.message.from_user.id,
        "Messaggio inviato!",
        reply_markup=ReplyKeyboardRemove(),
    )


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

    id_list: list[int] = [user.id for user in get_all_users()]
    context.job_queue.run_repeating(
        callback=send_announce_job,
        interval=10,
        first=1,
        data=AnnounceData(
            users_id_list=id_list, message=update.message.reply_to_message
        ),
        name=f"announce{update.message.id}",
    )


@dataclass
class AnnounceData:
    users_id_list: list[int]
    message: Message


async def send_announce_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    announce_data: AnnounceData = job.data
    users_id_list: list[int] = announce_data.users_id_list
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
