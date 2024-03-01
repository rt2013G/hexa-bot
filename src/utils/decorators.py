from telegram import Update
from telegram.ext import (
    ContextTypes
)
from datetime import datetime
from src.utils import logger as l

def with_logging(func):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        start_time = datetime.now()

        await func(update, context)
        
        if update.message is None:
            return
        
        time_ms = (datetime.now()-start_time).microseconds / 1000
        text = "" if update.message.text is None else update.message.text
        msg_to_send = f"""\nUsing function: "{func.__name__}"\nOn user message:\n"{text}"\n
From user @{update.message.from_user.username}, id: {update.message.from_user.id}.\nElapsed time: {time_ms}ms"""
        l.LOGS.append(msg_to_send)
    
    return handler
