import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.api import CardData, get_image_bytes
from app.cache import get_card_data, get_guess_game_rankings
from app.filters import MainGroupFilter, MarketGroupFilter
from app.logger import with_logging
from app.utils import clean_command_text, get_rankings_message_from_scores


def get_command_handlers() -> list:
    return [
        CommandHandler(
            "search", card_search_handler, filters.ChatType.PRIVATE | MainGroupFilter()
        ),
        CommandHandler("rankings", guess_game_rankings_handler, ~MarketGroupFilter()),
    ]


@with_logging
async def card_search_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    search_term = clean_command_text(update.message.text, "/search")
    if len(search_term) > 40:
        return
    card_data: CardData | None = await get_card_data(search_term)
    if card_data is None:
        await context.bot.send_message(
            update.message.from_user.id,
            f'La carta "{search_term}" non è stata trovata.',
        )
        return

    card_name = card_data.name
    if card_name is None:
        logging.log(
            logging.ERROR,
            "An unexpected error has occured while retrieving a cached card name.",
        )
        return
    bytes = get_image_bytes(card_data.image)

    await context.bot.send_photo(
        update.message.from_user.id,
        photo=bytes,
        caption=f"{card_name}\n\n{card_data.desc}",
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

    rankings = get_guess_game_rankings(length=length)
    rankings_message = get_rankings_message_from_scores(rankings)
    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text=f"Classifica dei primi {length} giocatori:\n{rankings_message}",
        disable_notification=True,
    )
