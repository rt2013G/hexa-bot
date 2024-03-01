from datetime import datetime, timedelta
from telegram.ext import (
    ContextTypes,
)
from src.cache import db_cache as c
from src.config import get_logging_channel_id

def clean_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for key in list(c.USERS_CACHE):
        if c.USERS_CACHE[key].time < datetime.now() - timedelta(minutes=30):
            del c.USERS_CACHE[key]
    print("cache cleaned")
