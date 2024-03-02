import sys

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from src.database.dbms import get_users, make_role, remove_role, update_user_dates
from src.filters import AdminFilter, ApprovalGroupFilter, DebugUserFilter
from src.utils.logger import with_logging
from src.utils.utils import clean_command_text, get_user_from_message_command, is_role


def get_admin_handlers() -> list:
    return [
        CommandHandler(
            "makeseller", make_seller, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler(
            "removeseller", remove_seller, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler("reject", remove_seller, AdminFilter() & ApprovalGroupFilter()),
        CommandHandler("makescammer", make_scammer, AdminFilter()),
        CommandHandler("removescammer", remove_scammer, AdminFilter()),
        CommandHandler("announce", announce, DebugUserFilter()),
        CommandHandler("resetdate", reset_date, AdminFilter()),
        CommandHandler("getid", get_id_by_username, AdminFilter()),
        CommandHandler("getusername", get_username_by_id, AdminFilter()),
        CommandHandler("makeadmin", make_admin, DebugUserFilter()),
        CommandHandler("removeadmin", remove_admin, DebugUserFilter()),
        CommandHandler(
            "shutdown", shutdown, DebugUserFilter() & filters.ChatType.PRIVATE
        ),
    ]


@with_logging
async def make_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/makeseller")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if is_role(user.id, "seller"):
        await update.message.reply_text(
            "Utente già venditore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    make_role(user.id, "seller")
    await update.message.reply_text(
        "Utente approvato come venditore!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Sei stato approvato come venditore, ora puoi vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


@with_logging
async def remove_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/removeseller")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if not is_role(user.id, "seller"):
        await update.message.reply_text(
            "L'utente non è un venditore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role(user.id, "seller")
    await update.message.reply_text(
        "L'utente non è più un venditore!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Non sei più un venditore, non puoi più vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def reject_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/reject")

    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
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
async def make_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/makescammer")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if is_role(user.id, "scammer"):
        await update.message.reply_text(
            "Utente già nella lista scammer!", reply_markup=ReplyKeyboardRemove()
        )
        return

    make_role(user.id, "scammer")
    await update.message.reply_text(
        "Utente inserito nella lista scammer!", reply_markup=ReplyKeyboardRemove()
    )


@with_logging
async def remove_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/removescammer")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if not is_role(user.id, "scammer"):
        await update.message.reply_text(
            "L'utente non è nella lista scammer!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role(user.id, "scammer")
    await update.message.reply_text(
        "L'utente non è più nella lista scammer!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Sei stato rimosso dalla lista scammer, ora puoi tornare a vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


@with_logging
async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = clean_command_text(update.message.text, "/announce")
    users = get_users()
    for user in users:
        await context.bot.send_message(
            user.id, message, reply_markup=ReplyKeyboardRemove()
        )


@with_logging
async def reset_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/resetdate")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return

    if not is_role(user.id, "seller"):
        await update.message.reply_text(
            "L'utente non è un venditore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    update_user_dates(user.id)
    await update.message.reply_text(
        f"Date di {user.username} resettate!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Le date del tuo vendo e cerco giornalieri sono state resettate, puoi inviare un altro post oggi!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def get_id_by_username(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/getid")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    await update.message.reply_text(
        f"id di @{user.username}: {user.id}", reply_markup=ReplyKeyboardRemove()
    )


async def get_username_by_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/getusername")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if user.username is None:
        await update.message.reply_text(
            "L'utente non ha uno username!", reply_markup=ReplyKeyboardRemove()
        )
        return
    await update.message.reply_text(
        f"Username di {user.id}: @{user.username}", reply_markup=ReplyKeyboardRemove()
    )


@with_logging
async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/makeadmin")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if is_role(user.id, "admin"):
        await update.message.reply_text(
            "Utente già admin!", reply_markup=ReplyKeyboardRemove()
        )
        return

    make_role(user.id, "admin")
    await update.message.reply_text(
        "Utente aggiunto come admin!", reply_markup=ReplyKeyboardRemove()
    )


@with_logging
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/removeadmin")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if not is_role(user.id, "admin"):
        await update.message.reply_text(
            "L'utente non è admin!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role(user.id, "admin")
    await update.message.reply_text(
        "L'utente non è più admin!", reply_markup=ReplyKeyboardRemove()
    )


async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Shutting down...", reply_markup=ReplyKeyboardRemove()
    )
    sys.exit(0)
