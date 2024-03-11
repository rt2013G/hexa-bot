from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.config import get_approval_id
from app.database import has_role
from app.utils import get_auth_code_from_id

CODE, VIDEO = range(2)


def get_auth_conv_handler() -> list:
    return [
        ConversationHandler(
            entry_points=[
                CommandHandler("seller", auth_seller_handler, filters.ChatType.PRIVATE)
            ],
            states={
                CODE: [
                    MessageHandler(
                        filters.Regex("^(Autenticazione)$"), auth_code_state_handler
                    ),
                    CommandHandler("annulla", auth_cancel_handler),
                ],
                VIDEO: [
                    MessageHandler(
                        filters.VIDEO | filters.VIDEO_NOTE, auth_video_state_handler
                    ),
                    CommandHandler("annulla", auth_cancel_handler),
                ],
            },
            fallbacks=[CommandHandler("annulla", auth_cancel_handler)],
        )
    ]


async def auth_cancel_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    await update.message.reply_text(
        "Operazione annullata.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def auth_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    if update.message.from_user.username is None:
        await update.message.reply_text(
            "Non hai uno @username, non puoi diventare seller.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    user_id = update.message.from_user.id
    if has_role(user_id, "seller"):
        await update.message.reply_text(
            "Sei già un venditore.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Usa /annulla per annullare l'operazione, altrimenti premi su Autenticazione.\n(E' necessario un @username per diventare seller!)\n\nNota bene: Premendo su Autenticazione stai acconsentendo al trattamento dei tuoi dati personali, per maggiori informazioni usa il comando /gdpr",
        reply_markup=ReplyKeyboardMarkup([["Autenticazione"]], one_time_keyboard=True),
    )

    return CODE


async def auth_code_state_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    await update.message.reply_text(
        f"Registra un video di te stesso mentre leggi il codice sottostante, mantenendo bene in vista un identificativo qualsiasi (carta d'identità, patente, etc.). Non è necessario inquadrare la faccia.\nUsa /annulla per annullare l'operazione.\n\n\n{get_auth_code_from_id(update.message.from_user.id)}"
    )
    return VIDEO


async def auth_video_state_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    await context.bot.forward_message(
        get_approval_id(), update.message.chat_id, update.message.message_id
    )
    await context.bot.send_message(
        get_approval_id(),
        f"Codice: {get_auth_code_from_id(update.message.from_user.id)}",
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
