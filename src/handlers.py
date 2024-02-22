from telegram import Update
from telegram.ext import (
    ContextTypes
)

async def start(update: Update, context: ContextTypes):
    await context.bot.send_message(update.message.chat_id, "start")