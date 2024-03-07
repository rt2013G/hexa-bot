import logging
from dataclasses import dataclass
from datetime import datetime

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.card_search import (
    CardDataEntry,
    get_bytes_from_image,
    get_card_data,
    get_cropped_image,
)
from src.filters import AdminFilter, MainGroupFilter
from src.utils import get_random_card_name, get_rankings_message_from_scores


@dataclass
class GameStateData:
    start_time: datetime
    chat_id: int
    users_scores: dict[int, int]
    guessed_cards: list[str]
    card_to_guess_name: str
    card_to_guess_data: CardDataEntry
    crop_level: int


GUESSING, SEND_CARD = range(2)


def get_guess_game_conv_handler() -> list:
    return [
        ConversationHandler(
            entry_points=[
                CommandHandler("guessthecard", start_game, MainGroupFilter())
            ],
            states={
                GUESSING: [
                    MessageHandler(
                        ~filters.COMMAND & filters.TEXT & MainGroupFilter(),
                        guess_handler,
                    )
                ],
                SEND_CARD: [],
            },
            fallbacks=[
                CommandHandler(
                    "stopgame", stop_game, MainGroupFilter() & AdminFilter()
                ),
            ],
            per_chat=True,
            per_user=False,
        )
    ]


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    card_data = get_card_data("Question")
    chat_id = update.message.chat.id
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=get_bytes_from_image(card_data.image),
        caption="Venghino signori e signore!\nSta per iniziare il Guess The Card, non mancate mi raccomando!",
    )
    time = datetime.now()
    card_name = get_random_card_name()
    card_data = get_card_data(card_name)
    while card_data is None:
        card_name = get_random_card_name()
        card_data = get_card_data(card_name)

    game_state_data = GameStateData(
        start_time=time,
        chat_id=chat_id,
        users_scores={},
        guessed_cards=[],
        card_to_guess_name=card_name,
        card_to_guess_data=card_data,
        crop_level=4,
    )
    context.job_queue.run_repeating(
        callback=send_card_handler,
        interval=15,
        first=1,
        data=game_state_data,
        name=str(chat_id),
    )
    context.bot_data[chat_id] = game_state_data
    return GUESSING


async def send_card_handler(context: ContextTypes.DEFAULT_TYPE) -> None:
    data: GameStateData = context.job.data
    while data.card_to_guess_data is None:
        card_name = get_random_card_name()
        data.card_to_guess_data = get_card_data(card_name)

    size = data.card_to_guess_data.image.size
    crop = data.crop_level if data.crop_level >= 0 else 0
    image_to_send = get_cropped_image(data.card_to_guess_data.image, crop).resize(size)

    if data.crop_level < 0:
        await context.bot.send_photo(
            data.chat_id,
            photo=get_bytes_from_image(image_to_send),
            caption=f"La carta era {data.card_to_guess_name}, nessuno ha indovinato!",
        )
        data.card_to_guess_name = get_random_card_name()
        data.card_to_guess_data = get_card_data(data.card_to_guess_name)
        data.crop_level = 4
        context.job.data = data
        return

    await context.bot.send_photo(
        data.chat_id,
        photo=get_bytes_from_image(image_to_send),
        caption="Guess the card!",
    )
    data.crop_level -= 1
    context.job.data = data


async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    if update.message is None or (
        update.message.reply_to_message is None
        or update.message.reply_to_message.from_user.is_bot is False
        or update.message.reply_to_message.from_user.id != context.bot.id
    ):
        return GUESSING

    guess_word = update.message.text
    if len(guess_word) > 50:
        return GUESSING

    chat_id = update.message.chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if jobs is None:
        logging.log(
            logging.ERROR,
            "There was an issue during the guess the card game. The send card job was missing.",
        )
        return GUESSING
    job = jobs[0]
    game_state_data: GameStateData = job.data

    user_id = update.message.from_user.id
    guess_data = get_card_data(guess_word)
    if guess_data is None or guess_data.desc != game_state_data.card_to_guess_data.desc:
        await update.message.reply_text(
            text="No!",
        )
        return GUESSING

    game_state_data.guessed_cards.append(game_state_data.card_to_guess_name)
    score_gained = (
        game_state_data.crop_level + 1 if game_state_data.crop_level >= 0 else 1
    )
    current_score: int | None = game_state_data.users_scores.get(user_id)
    if current_score is None:
        game_state_data.users_scores[user_id] = score_gained
    else:
        game_state_data.users_scores[user_id] += score_gained
    score_text_display = "punti" if score_gained > 1 else "punto"
    await update.message.reply_text(
        text=f'"{guess_word}" è corretto! Ti sei aggiudicato {score_gained} {score_text_display}!'
    )

    if len(game_state_data.guessed_cards) > 10:
        job.schedule_removal()
        rankings = get_rankings_message_from_scores(game_state_data.users_scores)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Il gioco è terminato! Classifica finale:\n{rankings}",
        )
        return ConversationHandler.END

    game_state_data.card_to_guess_name = get_random_card_name()
    game_state_data.card_to_guess_data = get_card_data(
        game_state_data.card_to_guess_name
    )
    game_state_data.crop_level = 4
    job.data = game_state_data
    return GUESSING


async def stop_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    pass
    return ConversationHandler.END
