from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.constants import Messages


def info_handlers() -> list[CommandHandler]:
    return [
        CommandHandler("start", start_handler, filters.ChatType.PRIVATE),
        CommandHandler("gdpr", gdpr_handler, filters.ChatType.PRIVATE),
    ]


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        update.message.from_user.id,
        Messages.START,
        reply_markup=ReplyKeyboardRemove(),
    )


async def gdpr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        update.message.from_user.id,
        Messages.GDPR,
        reply_markup=ReplyKeyboardRemove(),
    )
