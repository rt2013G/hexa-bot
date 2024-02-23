from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters
)
from src.filters import MainGroupFilter, MarketGroupFilter

def get_chat_handlers() -> list:
    return [
        MessageHandler(MainGroupFilter() & ~filters.COMMAND, on_main_msg),
        MessageHandler(MarketGroupFilter() & ~filters.COMMAND, on_market_msg),
    ]

async def on_main_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def on_market_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass