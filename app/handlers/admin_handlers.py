from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes

from app.cache import has_role, update_user_date
from app.constants import Dates, Roles
from app.filters import AdminFilter, ApprovalGroupFilter
from app.logger import with_logging
from app.utils import get_user_from_message_command


def get_admin_handlers() -> list:
    return [
        CommandHandler(
            "reject", reject_seller_handler, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler("resetdate", reset_date_handler, AdminFilter()),
    ]


async def reject_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/reject")

    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return

    if has_role(user.id, Roles.SELLER):
        await update.message.reply_text(
            "L'utente è già un venditore! Per rimuoverlo usa il comando /removeseller",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await update.message.reply_text(
        "L'utente è stato notificato del rifiuto.", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "La tua richiesta di diventare venditore è stata rifiutata, "
        + "controlla che l'identificativo inviato sia leggibile e che il video non sia capovolto. "
        + "Dopodiché usa nuovamente il comando /seller.",
        reply_markup=ReplyKeyboardRemove(),
    )


@with_logging
async def reset_date_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/resetdate")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
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
