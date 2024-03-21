from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes

from app.cache import has_role, insert_role, remove_role
from app.constants import Messages, Roles
from app.filters import AdminFilter, ApprovalGroupFilter, DebugUserFilter
from app.message_helpers import get_user_from_command_arg


def get_role_handlers() -> list[CommandHandler]:
    return [
        CommandHandler(
            "makeseller", make_seller_handler, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler(
            "removeseller", remove_seller_handler, AdminFilter() & ApprovalGroupFilter()
        ),
        CommandHandler("makescammer", make_scammer_handler, AdminFilter()),
        CommandHandler("removescammer", remove_scammer_handler, AdminFilter()),
        CommandHandler("makeadmin", make_admin_handler, DebugUserFilter()),
        CommandHandler("removeadmin", remove_admin_handler, DebugUserFilter()),
        CommandHandler(
            "makemod", make_moderator_handler, DebugUserFilter() | AdminFilter()
        ),
        CommandHandler(
            "removemod", remove_moderator_handler, DebugUserFilter() | AdminFilter()
        ),
    ]


async def make_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.SELLER):
        await update.message.reply_text(
            "Utente già venditore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    insert_role(id=user.id, role_name=Roles.SELLER)
    await update.message.reply_text(
        "Utente approvato come venditore!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Sei stato approvato come venditore, ora puoi vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def remove_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if not has_role(user.id, Roles.SELLER):
        await update.message.reply_text(
            "L'utente non è un venditore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role(id=user.id, role_name=Roles.SELLER)
    await update.message.reply_text(
        "L'utente non è più un venditore!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Non sei più un venditore, non puoi più vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def make_scammer_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.SCAMMER):
        await update.message.reply_text(
            "Utente già nella lista scammer!", reply_markup=ReplyKeyboardRemove()
        )
        return

    insert_role(id=user.id, role_name=Roles.SCAMMER)
    await update.message.reply_text(
        "Utente inserito nella lista scammer!", reply_markup=ReplyKeyboardRemove()
    )


async def remove_scammer_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if not has_role(user.id, Roles.SCAMMER):
        await update.message.reply_text(
            "L'utente non è nella lista scammer!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role(id=user.id, role_name=Roles.SCAMMER)
    await update.message.reply_text(
        "L'utente non è più nella lista scammer!", reply_markup=ReplyKeyboardRemove()
    )
    await context.bot.send_message(
        user.id,
        "Sei stato rimosso dalla lista scammer, ora puoi tornare a vendere nel gruppo market!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def make_admin_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.ADMIN):
        await update.message.reply_text(
            "Utente già admin!", reply_markup=ReplyKeyboardRemove()
        )
        return

    insert_role(id=user.id, role_name=Roles.ADMIN)
    await update.message.reply_text(
        "Utente aggiunto come admin!", reply_markup=ReplyKeyboardRemove()
    )


async def remove_admin_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if not has_role(user.id, Roles.ADMIN):
        await update.message.reply_text(
            "L'utente non è admin!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role(id=user.id, role_name=Roles.ADMIN)
    await update.message.reply_text(
        "L'utente non è più admin!", reply_markup=ReplyKeyboardRemove()
    )


async def make_moderator_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if has_role(user.id, Roles.MODERATOR):
        await update.message.reply_text(
            "Utente già moderatore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    insert_role(id=user.id, role_name=Roles.MODERATOR)
    await update.message.reply_text(
        "Utente aggiunto come moderatore!", reply_markup=ReplyKeyboardRemove()
    )


async def remove_moderator_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await update.message.reply_text(
            Messages.USER_NOT_FOUND, reply_markup=ReplyKeyboardRemove()
        )
        return
    if not has_role(user.id, Roles.MODERATOR):
        await update.message.reply_text(
            "L'utente non è moderatore!", reply_markup=ReplyKeyboardRemove()
        )
        return

    remove_role(id=user.id, role_name=Roles.MODERATOR)
    await update.message.reply_text(
        "L'utente non è più moderatore!", reply_markup=ReplyKeyboardRemove()
    )
