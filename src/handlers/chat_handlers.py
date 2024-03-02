from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from src.filters import AdminFilter, MainGroupFilter


def get_chat_handlers() -> list:
    return [
        MessageHandler(
            ~filters.COMMAND & MainGroupFilter() & ~AdminFilter(), main_msg_handler
        ),
    ]


async def main_msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def market_msg_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    pass


async def buy_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def feedback_post_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    pass
