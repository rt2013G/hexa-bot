from typing import Union

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from app.cache import has_role
from app.config import get_approval_id
from app.constants import Messages, Roles
from app.filters import AdminFilter, ApprovalGroupFilter
from app.message_helpers import get_user_from_command_arg

CODE, VIDEO = range(2)


def seller_auth_handlers() -> list[Union[ConversationHandler, CommandHandler]]:
    return [
        ConversationHandler(
            entry_points=[
                CommandHandler("seller", seller_handler, filters.ChatType.PRIVATE)
            ],
            states={
                CODE: [
                    MessageHandler(
                        filters.Regex("^(Autenticazione)$"), code_state_handler
                    ),
                    CommandHandler("annulla", cancel_handler),
                ],
                VIDEO: [
                    MessageHandler(
                        filters.VIDEO | filters.VIDEO_NOTE, video_state_handler
                    ),
                    CommandHandler("annulla", cancel_handler),
                ],
            },
            fallbacks=[CommandHandler("annulla", cancel_handler)],
        ),
        CommandHandler(
            "reject", reject_seller_handler, AdminFilter() & ApprovalGroupFilter()
        ),
    ]


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    await update.message.reply_text(
        "Operazione annullata.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def seller_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    if update.message.from_user.username is None:
        await update.message.reply_text(
            "Non hai uno @username, non puoi diventare seller.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    user_id = update.message.from_user.id
    if has_role(user_id, Roles.SELLER):
        await update.message.reply_text(
            "Sei già un venditore.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Usa /annulla per annullare l'operazione, altrimenti premi su Autenticazione.\n(E' necessario un @username per diventare seller!)\n\nNota bene: Premendo su Autenticazione stai acconsentendo al trattamento dei tuoi dati personali, per maggiori informazioni usa il comando /gdpr",
        reply_markup=ReplyKeyboardMarkup([["Autenticazione"]], one_time_keyboard=True),
    )

    return CODE


async def code_state_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    await update.message.reply_text(
        f"Registra un video di te stesso mentre leggi il codice sottostante, mantenendo bene in vista un identificativo qualsiasi (carta d'identità, patente, etc.). Non è necessario inquadrare la faccia.\nUsa /annulla per annullare l'operazione.\n\n\n{user_code(update.message.from_user.id)}"
    )
    return VIDEO


def user_code(user_id: int) -> int:
    return int(str(user_id**2)[0:6])


async def video_state_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    await context.bot.forward_message(
        get_approval_id(), update.message.chat_id, update.message.message_id
    )
    await context.bot.send_message(
        get_approval_id(),
        f"Codice: {user_code(update.message.from_user.id)}",
    )
    await context.bot.send_message(
        get_approval_id(),
        f"/makeseller {update.message.from_user.id}",
        reply_markup=ReplyKeyboardMarkup(
            [[f"/makeseller {update.message.from_user.id}"]], one_time_keyboard=True
        ),
    )
    await update.message.reply_text("Riceverai a breve una notifica di conferma.")
    return ConversationHandler.END


async def reject_seller_handler(
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
