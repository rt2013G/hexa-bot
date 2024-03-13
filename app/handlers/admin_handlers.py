import sys

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.constants import Roles
from app.database import (add_role_to_user, has_role, remove_role_from_user,
                          reset_user_buy_post, reset_user_sell_post)
from app.filters import AdminFilter, ApprovalGroupFilter, DebugUserFilter
from app.logger import with_logging
from app.utils import get_user_from_message_command


def get_admin_handlers() -> list:
    return [
        CommandHandler(
            "makeseller", make_seller_handler, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler(
            "removeseller", remove_seller_handler, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler(
            "reject", reject_seller_handler, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler("makescammer", make_scammer_handler, AdminFilter()),
        CommandHandler("removescammer", remove_scammer_handler, AdminFilter()),
        CommandHandler("resetdate", reset_date_handler, AdminFilter()),
        CommandHandler("getid", get_id_by_username_handler, AdminFilter()),
        CommandHandler("getusername", get_username_by_id_handler, AdminFilter()),
        CommandHandler("makeadmin", make_admin_handler, DebugUserFilter()),
        CommandHandler("removeadmin", remove_admin_handler, DebugUserFilter()),
        CommandHandler(
            "makemod", make_moderator_handler, DebugUserFilter() | AdminFilter()
        ),
        CommandHandler(
            "removemod", remove_moderator_handler, DebugUserFilter() | AdminFilter()
        ),
        CommandHandler(
            "shutdown", shutdown_handler, DebugUserFilter() & filters.ChatType.PRIVATE
        ),
    ]


@with_logging
async def make_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/makeseller")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.SELLER):
        await update.message.reply_text(
            "Utente già venditore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    add_role_to_user(id=user.id, role_name=Roles.SELLER)
    await update.message.reply_text(
        "Utente approvato come venditore!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Sei stato approvato come venditore, ora puoi vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


@with_logging
async def remove_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/removeseller")
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

    remove_role_from_user(id=user.id, role_name=Roles.SELLER)
    await update.message.reply_text(
        "L'utente non è più un venditore!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Non sei più un venditore, non puoi più vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


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
async def make_scammer_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/makescammer")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.SCAMMER):
        await update.message.reply_text(
            "Utente già nella lista scammer!", reply_markup=ReplyKeyboardRemove()
        )
        return

    add_role_to_user(id=user.id, role_name=Roles.SCAMMER)
    await update.message.reply_text(
        "Utente inserito nella lista scammer!", reply_markup=ReplyKeyboardRemove()
    )


@with_logging
async def remove_scammer_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/removescammer")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if not has_role(user.id, Roles.SCAMMER):
        await update.message.reply_text(
            "L'utente non è nella lista scammer!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role_from_user(id=user.id, role_name=Roles.SCAMMER)
    await update.message.reply_text(
        "L'utente non è più nella lista scammer!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Sei stato rimosso dalla lista scammer, ora puoi tornare a vendere nel gruppo market!",
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

    reset_user_buy_post(id=user.id)
    reset_user_sell_post(id=user.id)
    await update.message.reply_text(
        f"Date di {user.username} resettate!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Le date del tuo vendo e cerco giornalieri sono state resettate, puoi inviare un altro post oggi!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def get_id_by_username_handler(
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


async def get_username_by_id_handler(
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
async def make_admin_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/makeadmin")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.ADMIN):
        await update.message.reply_text(
            "Utente già admin!", reply_markup=ReplyKeyboardRemove()
        )
        return

    add_role_to_user(id=user.id, role_name=Roles.ADMIN)
    await update.message.reply_text(
        "Utente aggiunto come admin!", reply_markup=ReplyKeyboardRemove()
    )


@with_logging
async def remove_admin_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/removeadmin")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if not has_role(user.id, Roles.ADMIN):
        await update.message.reply_text(
            "L'utente non è admin!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role_from_user(id=user.id, role_name=Roles.ADMIN)
    await update.message.reply_text(
        "L'utente non è più admin!", reply_markup=ReplyKeyboardRemove()
    )


@with_logging
async def make_moderator_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/makemod")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.MODERATOR):
        await update.message.reply_text(
            "Utente già moderator!", reply_markup=ReplyKeyboardRemove()
        )
        return

    add_role_to_user(id=user.id, role_name=Roles.MODERATOR)
    await update.message.reply_text(
        "Utente aggiunto come moderatore!", reply_markup=ReplyKeyboardRemove()
    )


@with_logging
async def remove_moderator_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/removemod")
    if user is None:
        await update.message.reply_text(
            "Utente non trovato!", reply_markup=ReplyKeyboardRemove()
        )
        return
    if not has_role(user.id, Roles.MODERATOR):
        await update.message.reply_text(
            "L'utente non è moderatore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role_from_user(id=user.id, role_name=Roles.MODERATOR)
    await update.message.reply_text(
        "L'utente non è più moderatore!", reply_markup=ReplyKeyboardRemove()
    )


async def shutdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Shutting down...", reply_markup=ReplyKeyboardRemove()
    )
    sys.exit(0)
