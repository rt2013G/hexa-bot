from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)

def get_admin_handlers() -> list:
    return [
        
    ]

async def make_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def remove_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def reject_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def make_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def remove_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def get_id_by_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def get_username_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
