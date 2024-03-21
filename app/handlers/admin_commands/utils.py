import sys

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.constants import Messages
from app.filters import AdminFilter, DebugUserFilter
from app.message_helpers import get_user_from_command_arg


def get_utils_handlers() -> list[CommandHandler]:
    return [
        CommandHandler("info", get_user_info_handler, AdminFilter()),
        CommandHandler(
            "shutdown", shutdown_handler, DebugUserFilter() & filters.ChatType.PRIVATE
        ),
    ]


async def get_user_info_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
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
    await context.application.shutdown()
    sys.exit(0)
