from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)

def get_main_handlers() -> list:
    return [
        
    ]

async def on_main_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass