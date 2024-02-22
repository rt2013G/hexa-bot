from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)
from src.filters import AdminFilter, ApprovalGroupFilter

def get_admin_handlers() -> list:
    return [
        CommandHandler("makeseller", make_seller, AdminFilter & ApprovalGroupFilter),
        CommandHandler("removeseller", remove_seller, AdminFilter & ApprovalGroupFilter),
        CommandHandler("rejectseller", remove_seller, AdminFilter & ApprovalGroupFilter),
        CommandHandler("makescammer", make_scammer, AdminFilter & ApprovalGroupFilter),
        CommandHandler("removescammer", remove_scammer, AdminFilter & ApprovalGroupFilter),
        CommandHandler("getid", get_id_by_username, AdminFilter),
        CommandHandler("get_username", get_username_by_id, AdminFilter),
        CommandHandler("makeadmin", make_admin, False),
        CommandHandler("remove_admin", remove_admin, False),
        CommandHandler("announce", announce, False),
        CommandHandler("shutdown", shutdown, False),
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
