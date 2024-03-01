from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters
)
from src.filters import MainGroupFilter, AdminFilter
from src.database.dbms import get_user_from_id, insert_user, update_user_info
from src.cache.db_cache import insert_into_cache

def get_chat_handlers() -> list:
    return [
        MessageHandler(~filters.COMMAND & MainGroupFilter() & ~AdminFilter(), main_msg_handler),
    ]

async def main_msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = update.message.from_user.id
    user = get_user_from_id(id)
    if user is None:
        insert_user(id=id, 
                    username=update.message.from_user.username,
                    first_name=update.message.from_user.first_name,
                    last_name=update.message.from_user.last_name)
    else:
        update_user_info(id=id,
            username=update.message.from_user.username,
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name
        )     
    insert_into_cache(user=get_user_from_id(id), is_seller=False)

async def market_msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def buy_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def feedback_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass
