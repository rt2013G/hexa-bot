import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

# from app.card_search import (CardDataEntry, get_bytes_from_image,
#                             get_cached_card_name, get_card_data)
from app.config import get_market_group_link
from app.constants import Roles
# from app.database import User, get_top_guess_game_users, get_user, has_role
# from app.database.models.feedback import get_feedback_count, get_feedbacks
from app.filters import AdminFilter, MainGroupFilter, MarketGroupFilter
from app.logger import with_logging
from app.utils import (clean_command_text, get_rankings_message_from_scores,
                       get_user_from_message_command, has_sent_buy_post_today,
                       has_sent_sell_post_today)


def get_command_handlers() -> list:
    return [
        CommandHandler("start", start_handler, filters.ChatType.PRIVATE),
        CommandHandler(
            "search", card_search_handler, filters.ChatType.PRIVATE | MainGroupFilter()
        ),
        CommandHandler(
            "checkseller",
            check_seller_handler,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler(
            "checkscammer",
            check_scammer_handler,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler(
            "checkposts",
            check_posts_handler,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler("gdpr", gdpr_handler, filters.ChatType.PRIVATE),
        CommandHandler("feedback", feedback_list_handler, filters.ChatType.PRIVATE),
        CommandHandler("rankings", guess_game_rankings_handler, ~MarketGroupFilter()),
    ]


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
async def card_search_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
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
async def check_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/checkseller")
    if user is None:
        await context.bot.send_message(
            update.message.chat.id,
            "Utente non trovato! Assicurati di aver scritto correttamente lo @username.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if has_role(user.id, Roles.SELLER):
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
async def check_scammer_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
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


@with_logging
async def check_posts_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_message_command(update.message.text, "/checkposts")
    if user is None:
        await context.bot.send_message(
            update.message.chat.id,
            "Utente non trovato! Assicurati di aver scritto correttamente lo @username.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    buy_post_display = (
        "L'utente ha inviato un post di cerco oggi!"
        if has_sent_buy_post_today(user_id=user.id)
        else "L'utente NON ha inviato un post di cerco oggi!"
    )
    sell_post_display = ""
    if has_role(user.id, Roles.SELLER):
        sell_post_display = (
            "L'utente ha inviato un post di vendo oggi!"
            if has_sent_sell_post_today(user_id=user.id)
            else "L'utente NON ha inviato un post di vendo oggi!"
        )
    else:
        sell_post_display = "L'utente NON è un venditore!"

    await context.bot.send_message(
        update.message.chat.id,
        f"{buy_post_display}\n{sell_post_display}",
        reply_markup=ReplyKeyboardRemove(),
    )


async def gdpr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
async def feedback_list_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    seller = get_user_from_message_command(update.message.text, "/feedback")
    if seller is None:
        await context.bot.send_message(
            update.message.from_user.id,
            "Utente non trovato! Assicurati di aver scritto correttamente lo @username.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if not has_role(seller.id, Roles.SELLER):
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
            f'Feedback inviato da {buyer.username} in data {feedback.date.date()}:\n\n"{feedback.contents}"',
            reply_markup=ReplyKeyboardRemove(),
        )

    total_feedback_count = get_feedback_count(seller_id=seller.id)
    await context.bot.send_message(
        update.message.from_user.id,
        f"L'utente @{seller.username} ha {total_feedback_count} feedback in totale, eccone alcuni 👆👆",
        reply_markup=ReplyKeyboardRemove(),
    )


async def guess_game_rankings_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    length_text = clean_command_text(update.message.text, "/rankings")
    length = 10
    if len(length_text) > 0:
        try:
            length = int(length_text)
        except ValueError:
            return
    if length < 2:
        length = 10

    rankings = get_top_guess_game_users(length=length)
    rankings_message = get_rankings_message_from_scores(rankings)
    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text=f"Classifica dei primi {length} giocatori:\n{rankings_message}",
        disable_notification=True,
    )
