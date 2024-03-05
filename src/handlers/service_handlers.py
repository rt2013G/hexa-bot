from telegram import Update
from telegram.ext import ContextTypes, TypeHandler

from src.database import User, get_user, update_user_info
from src.database.models.user import insert_user


def get_service_handlers() -> list:
    return [TypeHandler(Update, user_update_handler)]


async def user_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None:
        return
    id = update.effective_user.id
    user: User | None = get_user(id=id)
    if user is None:
        insert_user(
            id=id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
        )
    else:
        update_user_info(
            id=id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
        )
