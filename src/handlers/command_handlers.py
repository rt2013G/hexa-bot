import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from src.card_search import CardDataEntry, get_cached_card_name, get_card_data
from src.config import get_market_group_link
from src.database import User, get_user, has_role
from src.database.models.feedback import get_feedbacks
from src.filters import AdminFilter, MainGroupFilter
from src.guess_the_card import get_bytes_from_image
from src.utils.logger import with_logging
from src.utils.utils import clean_command_text, get_user_from_message_command


def get_command_handlers() -> list:
    return [
        CommandHandler("start", start, filters.ChatType.PRIVATE),
        CommandHandler(
            "search", get_card_search, filters.ChatType.PRIVATE | MainGroupFilter()
        ),
        CommandHandler(
            "checkseller",
            check_seller,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler(
            "checkscammer",
            check_scammer,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler("gdpr", gdpr, filters.ChatType.PRIVATE),
        CommandHandler("feedback", get_feedback_list, filters.ChatType.PRIVATE),
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = f"""Benvenuto sul gruppo Yu-Gi-Oh ITA Main.
Per entrare nel gruppo market segui questo link: {get_market_group_link()}.\n
Ricorda di leggere le regole! Solo i venditori approvati possono vendere sul gruppo.
Se vuoi diventare venditore, usa il comando /seller.\n
Ricorda che in ogni caso, puoi effettuare solo 1 post di vendita e 1 post di acquisto al giorno."""
    await context.bot.send_message(
        update.message.from_user.id,
        msg,
        reply_markup=ReplyKeyboardRemove(),
    )


@with_logging
async def get_card_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_term = clean_command_text(update.message.text, "/search")
    if len(search_term) > 40:
        return
    card_data_entry: CardDataEntry | None = get_card_data(search_term)
    if card_data_entry is None:
        await context.bot.send_message(
            update.message.from_user.id,
            f'La carta "{search_term}" non è stata trovata.',
        )
        return

    card_name = get_cached_card_name(search_term)
    if card_name is None:
        logging.log(
            logging.ERROR,
            "An unexpected error has occured while retrieving a cached card name.",
        )
        return
    bytes = get_bytes_from_image(card_data_entry.image)

    await context.bot.send_photo(
        update.message.from_user.id,
        photo=bytes,
        caption=f"{card_name}\n\n{card_data_entry.desc}",
    )


@with_logging
async def check_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/checkseller")
    if user is None:
        await context.bot.send_message(
            update.message.chat.id,
            "Utente non trovato! Assicurati di aver scritto correttamente lo @username.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if has_role(user.id, "seller"):
        await context.bot.send_message(
            update.message.chat.id,
            "L'utente è un venditore!",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await context.bot.send_message(
            update.message.chat.id,
            "L'utente NON è un venditore!",
            reply_markup=ReplyKeyboardRemove(),
        )


@with_logging
async def check_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/checkscammer")
    if user is None:
        await context.bot.send_message(
            update.message.chat.id,
            "Utente non trovato! Assicurati di aver scritto correttamente lo @username.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if has_role(user.id, "scammer"):
        await context.bot.send_message(
            update.message.chat.id,
            "L'utente è uno scammer!",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await context.bot.send_message(
            update.message.chat.id,
            "L'utente NON è uno scammer!",
            reply_markup=ReplyKeyboardRemove(),
        )


async def gdpr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    gdpr_msg = """Al fine di limitare il numero di truffatori, per autenticarsi come seller è necessario fornire un identificativo.
Se non si vuole vendere sul gruppo, NON è ovviamente obbligatorio autenticarsi.
Il video inviatoci è visibile soltanto agli amministratori del gruppo market, e non viene salvato dal bot. Non è condiviso con nessun altro.
Il video non viene utilizzato per nessuno scopo ECCETTO in caso di truffa da parte di un venditore, in quel caso potrebbe essere utilizzato al fine di risalire all'identità del truffatore.
"""
    await context.bot.send_message(
        update.message.from_user.id,
        gdpr_msg,
        reply_markup=ReplyKeyboardRemove(),
    )


@with_logging
async def get_feedback_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    seller = get_user_from_message_command(update.message.text, "/feedback")
    if seller is None:
        await context.bot.send_message(
            update.message.from_user.id,
            "Utente non trovato! Assicurati di aver scritto correttamente lo @username.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if not has_role(seller.id, "seller"):
        await context.bot.send_message(
            update.message.from_user.id,
            "L'utente non è un venditore!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    feedbacks = get_feedbacks(seller.id)
    if len(feedbacks) == 0:
        await context.bot.send_message(
            update.message.from_user.id,
            "L'utente non ha feedback.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await context.bot.send_message(
        update.message.from_user.id,
        f"L'utente @{seller.username} ha {len(feedbacks)} feedback, eccone alcuni:",
        reply_markup=ReplyKeyboardRemove(),
    )
    for feedback in feedbacks:
        buyer: User | None = get_user(id=feedback.buyer_id)
        if buyer is None:
            continue
        if buyer.first_name is None:
            buyer.first_name = ""
        if buyer.last_name is None:
            buyer.last_name = ""
        if buyer.username is None:
            buyer.username = buyer.first_name + " " + buyer.last_name
        else:
            buyer.username = "@" + buyer.username
        await context.bot.send_message(
            update.message.from_user.id,
            f"Feedback inviato da {buyer.username} in data {feedback.date.date()}:",
            reply_markup=ReplyKeyboardRemove(),
        )
        await context.bot.send_message(
            update.message.from_user.id,
            f'"{feedback.contents}"',
            reply_markup=ReplyKeyboardRemove(),
        )
