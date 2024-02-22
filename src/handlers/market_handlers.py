from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)

def get_market_handlers() -> list:
    return [
        
    ]

async def on_market_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass
