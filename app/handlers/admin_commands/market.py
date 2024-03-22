from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes

from app.cache import has_role, update_user_date
from app.constants import Dates, Messages, Roles
from app.filters import AdminFilter
from app.message_helpers import get_user_from_command_arg


def market_handlers() -> list[CommandHandler]:
    return [
        CommandHandler("resetdate", reset_date_handler, AdminFilter()),
    ]


async def reset_date_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return

    if not has_role(user.id, Roles.SELLER):
        await update.message.reply_text(
            "L'utente non è un venditore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    update_user_date(
        id=user.id, last_buy_post=Dates.MARKET_EPOCH, last_sell_post=Dates.MARKET_EPOCH
    )
    await update.message.reply_text(
        f"Date di {user.username} resettate!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Le date del tuo vendo e cerco giornalieri sono state resettate, puoi inviare un altro post oggi!",
        reply_markup=ReplyKeyboardRemove(),
    )
