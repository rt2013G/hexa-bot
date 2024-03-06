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
from src.database import get_user
from src.filters import AdminFilter, MainGroupFilter
from src.utils.utils import get_random_card_name


@dataclass
class CurrentGameState:
    start_time: datetime
    chat_id: int
    user_scores: dict[int, int]
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
    message = await context.bot.send_photo(
        chat_id=chat_id,
        photo=get_bytes_from_image(card_data.image),
        caption="Venghino signori e signore!\nSta per iniziare il Guess The Card, non mancate mi raccomando!",
    )
    await context.bot.pin_chat_message(
        update.message.chat.id, message_id=message.id, disable_notification=False
    )
    time = datetime.now()
    card_name = get_random_card_name()
    card_data = get_card_data(card_name)
    while card_data is None:
        card_name = get_random_card_name()
        card_data = get_card_data(card_name)

    game_state_data = CurrentGameState(
        start_time=time,
        chat_id=chat_id,
        user_scores={},
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
    data: CurrentGameState = context.job.data
    while data.card_to_guess_data is None:
        card_name = get_random_card_name()
        data.card_to_guess_data = get_card_data(card_name)

    size = data.card_to_guess_data.image.size
    image_to_send = get_cropped_image(
        data.card_to_guess_data.image, data.crop_level
    ).resize(size)

    await context.bot.send_photo(
        data.chat_id,
        photo=get_bytes_from_image(image_to_send),
        caption="Guess the card!",
    )
    if data.crop_level > 0:
        data.crop_level -= 1
    else:
        await context.bot.send_photo(
            data.chat_id,
            photo=get_bytes_from_image(image_to_send),
            caption=f"La carta era {data.card_to_guess_name}, nessuno ha indovinato!",
        )
        data.guessed_cards.append(data.card_to_guess_name)
        data.card_to_guess_name = get_random_card_name()
        data.card_to_guess_data = get_card_data(data.card_to_guess_name)
        data.crop_level = 4

    context.job.data = data


async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    guess_word = update.message.text
    if len(guess_word) > 50:
        return GUESSING

    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    game_state_data: CurrentGameState = context.bot_data[chat_id]

    guess_data = get_card_data(guess_word)
    if (
        guess_data is not None
        and guess_data.desc == game_state_data.card_to_guess_data.desc
    ):
        job = context.job_queue.get_jobs_by_name(str(chat_id))[0]
        current_game_state: CurrentGameState = job.data
        current_game_state.guessed_cards.append(current_game_state.card_to_guess_name)

        score_gained = current_game_state.crop_level + 1
        current_score: int | None = current_game_state.user_scores.get(user_id)
        if current_score is None:
            current_game_state.user_scores[user_id] = score_gained
        else:
            current_game_state.user_scores[user_id] += score_gained
        display = "punti" if score_gained > 1 else "punto"
        await update.message.reply_text(
            text=f'"{guess_word}" è corretto! Ti sei aggiudicato {score_gained} {display}!'
        )

        if len(current_game_state.guessed_cards) > 20:
            job.schedule_removal()
            rankings = ""
            for key in sorted(
                current_game_state.user_scores,
                key=current_game_state.user_scores.get,
                reverse=True,
            ):
                value = current_game_state.user_scores[key]
                user = get_user(key)
                user_to_display = ""
                if user.username is None:
                    if user.first_name is not None and user.last_name is not None:
                        user_to_display = user.first_name + user.last_name
                    elif user.first_name is not None:
                        user_to_display = user.first_name
                    elif user.last_name is not None:
                        user_to_display = user.last_name
                else:
                    user_to_display = "@" + user.username

                rankings += f"{user_to_display}, punteggio: {value}\n"
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Il gioco è terminato! Classifica finale:\n{rankings}",
            )
            return ConversationHandler.END

        current_game_state.card_to_guess_name = get_random_card_name()
        current_game_state.card_to_guess_data = get_card_data(
            current_game_state.card_to_guess_name
        )
        current_game_state.crop_level = 4
        job.data = current_game_state

        return GUESSING

    await update.message.reply_text(
        text="No!",
    )
    return GUESSING


async def stop_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    pass
