from datetime import datetime, timedelta

from telegram.ext import ContextTypes

from app.constants import CacheLimits

from .card_data import search_cache
from .feedbacks import feedbacks_cache
from .game_data import games_cache
from .users import users_cache


async def users_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for user_id in list(users_cache.users.keys()):
        if users_cache.users[user_id].time < datetime.now() - timedelta(days=1):
            del users_cache.users[user_id]

    if len(users_cache.users) > CacheLimits.MAX_USER_SIZE:
        size = CacheLimits.MAX_USER_SIZE // 2
        for i, user_id in enumerate(list(users_cache.users.keys())):
            del users_cache.users[user_id]
            if i > size:
                break

    if len(users_cache.ids) > CacheLimits.MAX_USERNAME_SIZE:
        size = CacheLimits.MAX_USERNAME_SIZE // 2
        for i, username in enumerate(list(users_cache.ids.keys())):
            del users_cache.ids[username]
            if i > size:
                break


async def roles_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for user_id in list(users_cache.roles.keys()):
        if users_cache.roles[user_id].time < datetime.now() - timedelta(days=1):
            del users_cache.roles[user_id]

    if len(users_cache.roles) > CacheLimits.MAX_ROLE_SIZE:
        size = CacheLimits.MAX_ROLE_SIZE // 2
        for i, user_id in enumerate(list(users_cache.roles.keys())):
            del users_cache.roles[user_id]
            if i > size:
                break


async def feedbacks_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def card_data_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for card_name in list(search_cache.cards.keys()):
        if search_cache.cards[card_name].time < datetime.now() - timedelta(days=1):
            del search_cache.cards[card_name]

    if len(search_cache.cards) > CacheLimits.MAX_CARD_DATA_SIZE:
        size = CacheLimits.MAX_CARD_DATA_SIZE // 2
        for i, card_name in enumerate(list(search_cache.cards.keys())):
            del search_cache.cards[card_name]
            if i > size:
                break

    if len(search_cache.words) > CacheLimits.MAX_SEARCH_WORD_SIZE:
        size = CacheLimits.MAX_SEARCH_WORD_SIZE // 2
        for i, search_word in enumerate(list(search_cache.words.keys())):
            del search_cache.words[search_word]
            if i > size:
                break


async def games_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for length in list(games_cache.guess_game_rankings.keys()):
        if games_cache.guess_game_rankings[length].time < datetime.now() - timedelta(
            days=1
        ):
            del games_cache.guess_game_rankings[length]

    if len(games_cache.guess_game_rankings) > CacheLimits.MAX_GUESS_GAME_RANKINGS_SIZE:
        size = CacheLimits.MAX_GUESS_GAME_RANKINGS_SIZE // 2
        for i, length in enumerate(list(games_cache.guess_game_rankings.keys())):
            del games_cache.guess_game_rankings[length]
            if i > size:
                break
