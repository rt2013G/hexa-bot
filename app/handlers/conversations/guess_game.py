import asyncio
import json
import logging
import os
import random
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher

import requests
from telegram import Message, ReactionTypeEmoji, Update
from telegram.constants import ReactionEmoji
from telegram.error import BadRequest, Forbidden, TimedOut
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.api import CardData, get_cropped_image, get_image_bytes
from app.cache import get_card_data, insert_guess_game_scores
from app.constants import GuessGame
from app.filters import ModeratorFilter
from app.message_helpers import (
    get_rankings_message_from_scores,
    remove_non_alpha_characters,
)


@dataclass
class GameStateData:
    start_time: datetime
    chat_id: int
    users_scores: dict[int, int]
    guessed_cards: list[str]
    messages_to_delete: list[Message]
    card_to_guess_name: str
    card_to_guess_data: CardData | None
    crop_level: int


GUESSING = range(1)


def guess_game_conv_handler() -> list[ConversationHandler]:
    return [
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "guessthecard",
                    guess_the_card_handler,
                    filters.ChatType.GROUPS & ModeratorFilter(),
                )
            ],
            states={
                GUESSING: [
                    MessageHandler(
                        ~filters.COMMAND & filters.TEXT & filters.ChatType.GROUPS,
                        guess_handler,
                    )
                ],
            },
            fallbacks=[
                CommandHandler(
                    "stopgame",
                    stop_game_handler,
                    filters.ChatType.GROUPS & ModeratorFilter(),
                ),
            ],
            per_chat=True,
            per_user=False,
        )
    ]


async def guess_the_card_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    await load_card_name_db()
    card_data = await get_card_data("Question")
    chat_id = update.message.chat.id
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=get_image_bytes(card_data.image),
        caption="Venghino signori e signore!\nSta per iniziare il Guess The Card, non mancate mi raccomando!",
    )

    game_state_data = GameStateData(
        start_time=datetime.now(),
        chat_id=chat_id,
        users_scores={},
        guessed_cards=[],
        messages_to_delete=[],
        card_to_guess_name="",
        card_to_guess_data=None,
        crop_level=4,
    )
    context.job_queue.run_repeating(
        callback=send_card_job,
        interval=15,
        first=15,
        data=game_state_data,
        name=str(chat_id),
    )
    context.bot_data[chat_id] = game_state_data
    return GUESSING


async def load_card_name_db() -> None:
    path = "app/static/card_names.json"
    if not os.path.exists(os.path.abspath(path)):
        CARD_NAME_URL = "https://db.ygorganization.com/data/idx/card/name/en"
        response = await asyncio.to_thread(requests.get, url=CARD_NAME_URL, timeout=10)
        response_json = json.loads(response.content)
        with open(os.path.abspath(path), "w") as f:
            json.dump(response_json, f)


def get_random_card_name() -> str:
    path = "app/static/card_names.json"
    card_database: dict[str, list[int]]
    with open(os.path.abspath(path), "r") as f:
        card_database = dict(json.load(f))

    # trunk-ignore(bandit/B311)
    return random.choice(list(card_database.keys()))


async def send_card_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data: GameStateData = context.job.data
    while (
        data.card_to_guess_data is None
        or data.card_to_guess_name is None
        or len(data.card_to_guess_name) == 0
    ):
        data.card_to_guess_name = get_random_card_name()
        data.card_to_guess_data = await get_card_data(data.card_to_guess_name)

    data.card_to_guess_name = data.card_to_guess_data.name

    size = data.card_to_guess_data.image.size
    crop = data.crop_level if data.crop_level >= 0 else 0
    image_to_send = get_cropped_image(data.card_to_guess_data.image, crop).resize(size)

    if data.crop_level < 0:
        message_to_delete = await context.bot.send_photo(
            data.chat_id,
            photo=get_image_bytes(image_to_send),
            caption=f"La carta era {data.card_to_guess_name}, nessuno ha indovinato!",
        )

        data.messages_to_delete.append(message_to_delete)
        data.card_to_guess_name = ""
        data.card_to_guess_data = None
        data.crop_level = 4
        context.job.schedule_removal()
        context.job_queue.run_repeating(
            callback=send_card_job,
            interval=15,
            first=10,
            data=data,
            name=str(data.chat_id),
        )
        return

    message_to_delete = await context.bot.send_photo(
        data.chat_id,
        photo=get_image_bytes(image_to_send),
        caption="Guess the card!",
    )
    data.crop_level -= 1
    data.messages_to_delete.append(message_to_delete)
    context.job.data = data


async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> object:
    if (
        update.message is None
        or update.message.reply_to_message is None
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
    game_state_data.messages_to_delete.append(update.message)

    user_id = update.message.from_user.id
    guess = remove_non_alpha_characters(guess_word).lower()
    answer = remove_non_alpha_characters(game_state_data.card_to_guess_name).lower()
    correctness = SequenceMatcher(None, guess, answer).ratio()

    if correctness < GuessGame.CORRECT_THRESHOLD:
        await update.message.set_reaction(
            reaction=ReactionTypeEmoji(ReactionEmoji.THUMBS_DOWN)
        )
        return GUESSING

    game_state_data.guessed_cards.append(game_state_data.card_to_guess_name)
    score_gained = game_state_data.crop_level + 2
    current_score: int | None = game_state_data.users_scores.get(user_id)
    if current_score is None:
        game_state_data.users_scores[user_id] = score_gained
    else:
        game_state_data.users_scores[user_id] += score_gained
    score_text_display = "punti" if score_gained > 1 else "punto"
    await update.message.set_reaction(reaction=ReactionTypeEmoji(ReactionEmoji.FIRE))
    await update.message.reply_text(
        text=f'"{game_state_data.card_to_guess_name}" è corretto! Ti sei aggiudicato {score_gained} {score_text_display}!'
    )

    if len(game_state_data.guessed_cards) >= GuessGame.GAME_LENGTH:
        job.schedule_removal()
        insert_guess_game_scores(
            game_time=game_state_data.start_time,
            scores=game_state_data.users_scores,
        )
        rankings = get_rankings_message_from_scores(game_state_data.users_scores)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Il gioco è terminato! Classifica finale:\n{rankings}",
        )
        context.job_queue.run_repeating(
            callback=chat_cleaner_job,
            interval=5,
            first=1,
            data=game_state_data,
            name=str(chat_id) + "cleaner",
        )

        return ConversationHandler.END

    game_state_data.card_to_guess_name = ""
    game_state_data.card_to_guess_data = None
    game_state_data.crop_level = 4
    job.schedule_removal()
    context.job_queue.run_repeating(
        callback=send_card_job,
        interval=15,
        first=10,
        data=game_state_data,
        name=str(game_state_data.chat_id),
    )
    return GUESSING


async def chat_cleaner_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data: GameStateData = context.job.data
    for message in list(data.messages_to_delete):
        timed_out = False
        try:
            await message.delete()
        except TimedOut:
            timed_out = True
        except (Forbidden, BadRequest):
            pass
        if not timed_out:
            data.messages_to_delete.remove(message)
    if len(data.messages_to_delete) <= 0:
        context.job.schedule_removal()
    context.job.data = data


async def stop_game_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    chat_id = update.message.chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if jobs is None:
        logging.log(
            logging.ERROR,
            "There was an issue during the guess the card game. The send card job was missing.",
        )
        return ConversationHandler.END
    job = jobs[0]
    context.job_queue.run_repeating(
        callback=chat_cleaner_job,
        interval=5,
        first=1,
        data=job.data,
        name=str(chat_id) + "cleaner",
    )
    job.schedule_removal()
    await update.message.reply_text(text="Gioco terminato!")
    return ConversationHandler.END
