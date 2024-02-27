from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)
from src.filters import AdminFilter, ApprovalGroupFilter, DebugUserFilter, AnnounceFilter
from src.utils.decorators import with_logging
from src.utils.utils import get_user_from_message_command, is_role
from src.database.dbms import make_role

def get_admin_handlers() -> list:
    return [
        CommandHandler("makeseller", make_seller, AdminFilter() & ApprovalGroupFilter()),
        CommandHandler("removeseller", remove_seller, AdminFilter() & ApprovalGroupFilter()),
        CommandHandler("rejectseller", remove_seller, AdminFilter() & ApprovalGroupFilter()),
        CommandHandler("makescammer", make_scammer, AdminFilter() & ApprovalGroupFilter()),
        CommandHandler("removescammer", remove_scammer, AdminFilter() & ApprovalGroupFilter()),
        CommandHandler("announce", announce, AnnounceFilter()),
        CommandHandler("resetdate", make_reset_date, AdminFilter()),
        CommandHandler("getid", get_id_by_username, AdminFilter()),
        CommandHandler("getusername", get_username_by_id, AdminFilter()),
        CommandHandler("makeadmin", make_admin, DebugUserFilter()),
        CommandHandler("remove_admin", remove_admin, DebugUserFilter()),
        CommandHandler("shutdown", shutdown, DebugUserFilter()),
    ]

@with_logging
async def make_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_message_command(update.message.text, "/makeseller")
    if user is None:
        await update.message.reply_text("Utente non trovato!", 
                                        reply_markup=ReplyKeyboardRemove())
        return
    if is_role(user.id, "seller"):
        await update.message.reply_text("Utente già venditore!", 
                                        reply_markup=ReplyKeyboardRemove())
        return
    
    make_role(user.id, "seller")
    await update.message.reply_text("Utente approvato come venditore!", 
                                    reply_markup=ReplyKeyboardRemove())
    await context.bot.send_message(user.id, 
                                   "Sei stato approvato come venditore, ora puoi vendere nel gruppo market!", 
                                   reply_markup=ReplyKeyboardRemove())


async def remove_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def reject_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def make_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def remove_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def make_reset_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def get_id_by_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def get_username_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
