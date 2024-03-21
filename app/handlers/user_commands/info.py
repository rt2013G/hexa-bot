from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.api import get_image_bytes
from app.cache import CardData, get_card_data, get_guess_game_rankings
from app.constants import Messages
from app.filters import MarketGroupFilter
from app.message_helpers import get_rankings_message_from_scores


def info_handlers() -> list[CommandHandler]:
    return [
        CommandHandler("start", start_handler, filters.ChatType.PRIVATE),
        CommandHandler("gdpr", gdpr_handler, filters.ChatType.PRIVATE),
        CommandHandler("search", card_search_handler, ~MarketGroupFilter()),
        CommandHandler("rankings", guess_game_rankings_handler, ~MarketGroupFilter()),
    ]


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        update.message.from_user.id,
        Messages.START,
        reply_markup=ReplyKeyboardRemove(),
    )


async def gdpr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        update.message.from_user.id,
        Messages.GDPR,
        reply_markup=ReplyKeyboardRemove(),
    )


async def card_search_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    search_term = " ".join(context.args)
    if len(search_term) > 40:
        return
    card_data: CardData | None = await get_card_data(search_term)
    if card_data is None:
        await context.bot.send_message(
            update.message.from_user.id,
            f'La carta "{search_term}" non è stata trovata.',
        )
        return

    await context.bot.send_photo(
        update.message.from_user.id,
        photo=get_image_bytes(card_data.image),
        caption=f"{card_data.name}\n\n{card_data.desc}",
    )


async def guess_game_rankings_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    length = 10
    if len(context.args) == 1 and context.args[0].isdigit():
        length = int(context.args[0])
    if length < 2:
        length = 10

    rankings = get_guess_game_rankings(length=length)
    rankings_message = get_rankings_message_from_scores(rankings)
    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text=f"Classifica dei primi {length} giocatori:\n{rankings_message}",
        disable_notification=True,
    )
