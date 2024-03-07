import logging
from datetime import datetime

from telegram import Update
from telegram.error import Forbidden, TimedOut
from telegram.ext import ContextTypes

from src.config import get_logging_channel_id

LOGS: list[str]


def set_up_logger() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    global LOGS
    LOGS = []


def with_logging(func):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        start_time = datetime.now()

        await func(update, context)

        if update.message is None:
            return

        time_ms = (datetime.now() - start_time).microseconds / 1000
        text = "" if update.message.text is None else update.message.text
        msg_to_send = f"""\nUsing function: "{func.__name__}"\nOn user message:\n"{text}"\n
From user @{update.message.from_user.username}, id: {update.message.from_user.id}.\nElapsed time: {time_ms}ms"""
        LOGS.append(msg_to_send)

    return handler


async def post_logs_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(LOGS) == 0:
        return
    for message in list(LOGS):
        timed_out = False
        try:
            await context.bot.send_message(
                chat_id=get_logging_channel_id(), text=message
            )
        except (TimedOut, Forbidden):
            timed_out = True

        if timed_out:
            return
        else:
            LOGS.remove(message)
