from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)

def get_command_handlers() -> list:
    return [
        CommandHandler("start", start, filters=filters.ChatType.PRIVATE)
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def get_card_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def check_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def check_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def gdpr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def get_feedback_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass
