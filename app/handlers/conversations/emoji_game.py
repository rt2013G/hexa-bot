import json
import logging
import os
import random
from dataclasses import dataclass
from datetime import datetime

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

from app.api import get_image_bytes
from app.cache import get_card_data, insert_guess_game_scores
from app.constants import GuessGame
from app.filters import MarketGroupFilter, ModeratorFilter
from app.message_helpers import (
    get_rankings_message_from_scores,
    remove_non_alpha_characters,
)


@dataclass
class GameStateData:
    start_time: datetime
    chat_id: int
    users_scores: dict[int, int]
    guessed_archetypes: list[str]
    messages_to_delete: list[Message]
    emoji_database: dict[str, list[str]]
    archetype_name: str
    archetype_emoji: list[str]
    current_emoji_index: int


GUESSING = range(1)


def emoji_game_conv_handler() -> list[ConversationHandler]:
    return [
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "guessemoji",
                    emoji_game_handler,
                    filters.ChatType.GROUPS & ~MarketGroupFilter() & ModeratorFilter(),
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


async def emoji_game_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> object:
    card_data = await get_card_data("Reasoning")
    chat_id = update.message.chat.id
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=get_image_bytes(card_data.image),
        caption="👍👍👍👍👍👍👍\n🔜🔜🔜🔜🔜, 🤙🤙🤙🤙🤙🤙",
    )

    game_state_data = GameStateData(
        start_time=datetime.now(),
        chat_id=chat_id,
        users_scores={},
        guessed_archetypes=[],
        messages_to_delete=[],
        emoji_database=load_emoji_db(),
        archetype_name="",
        archetype_emoji=[],
        current_emoji_index=1,
    )
    context.job_queue.run_repeating(
        callback=send_archetype_job,
        interval=15,
        first=15,
        data=game_state_data,
        name=str(chat_id),
    )
    context.bot_data[chat_id] = game_state_data
    return GUESSING


def load_emoji_db() -> dict[str, list[str]]:
    path = "app/static/emoji_database.json"
    emoji_database: dict[str, list[str]]
    with open(os.path.abspath(path), "r") as f:
        emoji_database = dict(json.load(f))

    return emoji_database


def get_random_archetype_name(db: dict[str, list[str]]) -> str:
    # trunk-ignore(bandit/B311)
    return random.choice(list(db.keys()))


async def send_archetype_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data: GameStateData = context.job.data
    while (
        len(data.archetype_name) == 0 or data.archetype_name in data.guessed_archetypes
    ):
        data.archetype_name = get_random_archetype_name(data.emoji_database)

    if len(data.archetype_emoji) == 0:
        data.archetype_emoji = data.emoji_database.get(data.archetype_name)
        random.shuffle(data.archetype_emoji)

    if data.current_emoji_index > 6:
        message_to_delete = await context.bot.send_message(
            chat_id=data.chat_id,
            text=f"L'archetipo era {data.archetype_name}, nessuno ha indovinato!",
        )

        data.messages_to_delete.append(message_to_delete)
        data.archetype_name = ""
        data.archetype_emoji = []
        data.current_emoji_index = 1
        context.job.schedule_removal()
        context.job_queue.run_repeating(
            callback=send_archetype_job,
            interval=15,
            first=10,
            data=data,
            name=str(data.chat_id),
        )
        return

    emoji_text = " ".join(data.archetype_emoji[0 : data.current_emoji_index])
    message_text = f"Guess the archetype!\n\n{emoji_text}"
    message_to_delete = await context.bot.send_message(
        chat_id=data.chat_id, text=message_text
    )
    data.current_emoji_index += 1
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
            "There was an issue during the emoji game. The send archetype job was missing.",
        )
        return GUESSING
    job = jobs[0]
    game_state_data: GameStateData = job.data
    game_state_data.messages_to_delete.append(update.message)

    user_id = update.message.from_user.id
    guess = remove_non_alpha_characters(guess_word).lower()
    answer = remove_non_alpha_characters(game_state_data.archetype_name).lower()

    if guess != answer or len(answer) <= 1:
        await update.message.set_reaction(
            reaction=ReactionTypeEmoji(ReactionEmoji.THUMBS_DOWN)
        )
        return GUESSING

    game_state_data.guessed_archetypes.append(game_state_data.archetype_name)
    score_gained = 8 - game_state_data.current_emoji_index
    current_score: int | None = game_state_data.users_scores.get(user_id)
    if current_score is None:
        game_state_data.users_scores[user_id] = score_gained
    else:
        game_state_data.users_scores[user_id] += score_gained
    score_text_display = "punti" if score_gained > 1 else "punto"
    await update.message.set_reaction(reaction=ReactionTypeEmoji(ReactionEmoji.FIRE))
    await update.message.reply_text(
        text=f'"{game_state_data.archetype_name}" è corretto! Ti sei aggiudicato {score_gained} {score_text_display}!'
    )

    if len(game_state_data.guessed_archetypes) >= GuessGame.GAME_LENGTH:
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

    game_state_data.archetype_name = ""
    game_state_data.archetype_emoji = []
    game_state_data.current_emoji_index = 1
    job.schedule_removal()
    context.job_queue.run_repeating(
        callback=send_archetype_job,
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
            "There was an issue during the emoji game. The send archetype job was missing.",
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
