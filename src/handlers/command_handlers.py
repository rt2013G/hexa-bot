from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters
)
from src.filters import MainGroupFilter, AdminFilter
from src.config import get_market_group_link
from src.database.dbms import get_user_from_id, insert_user

def get_command_handlers() -> list:
    return [
        CommandHandler("start", start, filters.ChatType.PRIVATE),
        CommandHandler("search", get_card_search, filters.ChatType.PRIVATE | MainGroupFilter()),
        CommandHandler("checkseller", check_seller, filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter()),
        CommandHandler("checkscammer", check_scammer, filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter()),
        CommandHandler("gdpr", gdpr, filters.ChatType.PRIVATE),
        CommandHandler("feedback", get_feedback_list, filters.ChatType.PRIVATE),
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = update.message.from_user.id
    msg = f"""Benvenuto sul gruppo Yu-Gi-Oh ITA Main.
Per entrare nel gruppo market segui questo link: {get_market_group_link()}.\n
Ricorda di leggere le regole! Solo i venditori approvati possono vendere sul gruppo.
Se vuoi diventare venditore, usa il comando /seller.\n
Ricorda che in ogni caso, puoi effettuare solo 1 post di vendita e 1 post di acquisto al giorno."""
    await context.bot.send_message(id, msg, disable_web_page_preview=True)
    
    user = get_user_from_id(id)
    if user is None:
        insert_user(id=id, 
                    username=update.message.from_user.username,
                    first_name=update.message.from_user.first_name,
                    last_name=update.message.from_user.last_name)

async def get_card_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def check_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def check_scammer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def gdpr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    gdpr_msg = f"""Al fine di limitare il numero di truffatori, per autenticarsi come seller è necessario fornire un identificativo.
Se non si vuole vendere sul gruppo, NON è ovviamente obbligatorio autenticarsi.
Il video inviatoci è visibile soltanto agli amministratori del gruppo market, e viene salvato dal bot. Non è condiviso con nessun altro.
Il video non viene utilizzato per nessuno scopo ECCETTO in caso di truffa da parte di un venditore, in quel caso potrebbe essere utilizzato al fine di risalire all'identità del truffatore.
"""
    await context.bot.send_message(update.message.from_user.id, gdpr_msg, disable_web_page_preview=True)

async def get_feedback_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass
