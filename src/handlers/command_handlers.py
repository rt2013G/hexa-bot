from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)
from src.filters import MainGroupFilter, AdminFilter
from src.database import insert_user, get_user_from_id

def get_command_handlers() -> list:
    return [
        CommandHandler("start", start, filters.ChatType.PRIVATE),
        CommandHandler("search", get_card_search, filters.ChatType.PRIVATE | MainGroupFilter()),
        CommandHandler("checkseller", get_card_search, filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter()),
        CommandHandler("checkscammer", get_card_search, filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter()),
        CommandHandler("gdpr", gdpr, filters.ChatType.PRIVATE),
        CommandHandler("feedback", get_feedback_list, filters.ChatType.PRIVATE),
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
