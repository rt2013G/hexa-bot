from datetime import datetime, timedelta

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.config import get_market_plus_id
from app.database.models.market_plus_post import insert_market_plus_post
from app.filters import AdminFilter
from app.utils import clean_command_text


def get_market_plus_handlers() -> list:
    return [
        CommandHandler(
            "marketplus", market_plus_handler, filters.ChatType.PRIVATE & AdminFilter()
        )
    ]


async def market_plus_handler(
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
            "Per inviare un messaggio nel market plus, scrivi prima il messaggio, dopodiché rispondi ad esso con /marketplus <durata in ore>.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    try:
        hours = int(clean_command_text(update.message.text, "/marketplus"))
    except ValueError:
        await context.bot.send_message(
            update.message.from_user.id,
            "Per inviare un messaggio nel market plus, scrivi prima il messaggio, dopodiché rispondi ad esso con /marketplus <durata in ore>.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    forwarded_message = await update.message.reply_to_message.forward(
        chat_id=get_market_plus_id()
    )
    end_date = datetime.now() + timedelta(hours=hours)
    insert_market_plus_post(message_id=forwarded_message.id, end_date=end_date)
    await context.bot.send_message(
        update.message.from_user.id,
        "Messaggio market plus inviato correttamente!",
        reply_markup=ReplyKeyboardRemove(),
    )
