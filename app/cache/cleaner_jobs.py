from telegram.ext import ContextTypes

from .card_data import card_data_cache
from .feedbacks import feedbacks_cache
from .game_data import games_cache
from .users import users_cache


async def users_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def feedbacks_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def card_data_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def games_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass
