from datetime import datetime, timedelta
from telegram.ext import (
    ContextTypes,
)
from src.cache import db_cache as c
from src.config import get_logging_channel_id
from src.utils import logger as l
import logging


def clean_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for key in list(c.USERS_CACHE):
        if c.USERS_CACHE[key].time < datetime.now() - timedelta(minutes=30):
            del c.USERS_CACHE[key]
    logging.log(logging.INFO, "Cache cleaned")


async def post_logs_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(l.LOGS) == 0:
        return
    for message in list(l.LOGS):
        timed_out = False
        try:
            await context.bot.send_message(
                chat_id=get_logging_channel_id(), 
                text=message)
        except:
            timed_out = True

        if timed_out:
            return
        else:
            l.LOGS.remove(message)