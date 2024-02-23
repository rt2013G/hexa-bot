from telegram import Update
from telegram.ext import (
    ContextTypes
)
from src.utils.config import get_logging_channel_id
from datetime import datetime

def with_logging(func):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        start_time = datetime.now()
        await func(update, context)
        time_ms = (datetime.now()-start_time).microseconds / 1000
        msg_to_send = f"""Using function: "{func.__name__}"\nOn user message:\n{update.message.text}\nFrom user {update.message.from_user.username}.\n
Elapsed time: {time_ms}ms"""
        await context.bot.send_message(
            get_logging_channel_id(), 
            msg_to_send
            )
    
    return handler
