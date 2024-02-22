from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters
)
from src.filters import MainGroupFilter

def get_main_handlers() -> list:
    return [
        MessageHandler(MainGroupFilter & ~filters.COMMAND, on_main_msg)
    ]

async def on_main_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass