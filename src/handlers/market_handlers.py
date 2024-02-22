from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters
)
from src.filters import MainGroupFilter

def get_market_handlers() -> list:
    return [
        MessageHandler(MainGroupFilter & ~filters.COMMAND, on_market_msg),
    ]

async def on_market_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass
