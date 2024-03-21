from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.cache import get_feedbacks, get_user, has_role
from app.constants import Messages, Roles
from app.database import User
from app.filters import AdminFilter, MainGroupFilter
from app.message_helpers import get_user_from_command_arg
from app.utils import has_sent_buy_post_today, has_sent_sell_post_today


def market_handlers() -> list[CommandHandler]:
    return [
        CommandHandler(
            "checkseller",
            check_seller_handler,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler(
            "checkscammer",
            check_scammer_handler,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler(
            "checkposts",
            check_posts_handler,
            filters.ChatType.PRIVATE | MainGroupFilter() | AdminFilter(),
        ),
        CommandHandler("feedback", feedback_list_handler, filters.ChatType.PRIVATE),
    ]


async def check_seller_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await context.bot.send_message(
            update.message.chat.id,
            Messages.USER_NOT_FOUND_WITH_MENTION,
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if has_role(user.id, Roles.SELLER):
        await context.bot.send_message(
            update.message.chat.id,
            "L'utente è un venditore!",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await context.bot.send_message(
            update.message.chat.id,
            Messages.USER_NOT_SELLER,
            reply_markup=ReplyKeyboardRemove(),
        )


async def check_scammer_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await context.bot.send_message(
            update.message.chat.id,
            Messages.USER_NOT_FOUND_WITH_MENTION,
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if has_role(user.id, Roles.SCAMMER):
        await context.bot.send_message(
            update.message.chat.id,
            "L'utente è uno scammer!",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await context.bot.send_message(
            update.message.chat.id,
            "L'utente non è uno scammer!",
            reply_markup=ReplyKeyboardRemove(),
        )


async def check_posts_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    user = get_user_from_command_arg(arg=context.args[0])
    if user is None:
        await context.bot.send_message(
            update.message.chat.id,
            Messages.USER_NOT_FOUND_WITH_MENTION,
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    buy_post_display = (
        "L'utente ha inviato un post di cerco oggi!"
        if has_sent_buy_post_today(user_id=user.id)
        else "L'utente NON ha inviato un post di cerco oggi!"
    )
    sell_post_display = ""
    if has_role(user.id, Roles.SELLER):
        sell_post_display = (
            "L'utente ha inviato un post di vendo oggi!"
            if has_sent_sell_post_today(user_id=user.id)
            else "L'utente NON ha inviato un post di vendo oggi!"
        )
    else:
        sell_post_display = Messages.USER_NOT_SELLER

    await context.bot.send_message(
        update.message.chat.id,
        f"{buy_post_display}\n{sell_post_display}",
        reply_markup=ReplyKeyboardRemove(),
    )


async def feedback_list_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if len(context.args) == 0:
        return

    seller = get_user_from_command_arg(arg=context.args[0])
    if seller is None:
        await context.bot.send_message(
            update.message.from_user.id,
            Messages.USER_NOT_FOUND_WITH_MENTION,
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if not has_role(seller.id, Roles.SELLER):
        await context.bot.send_message(
            update.message.from_user.id,
            Messages.USER_NOT_SELLER,
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    feedbacks = get_feedbacks(seller.id)
    if len(feedbacks) == 0:
        await context.bot.send_message(
            update.message.from_user.id,
            "L'utente non ha feedback.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    for feedback in feedbacks:
        buyer: User | None = get_user(id=feedback.buyer_id)
        if buyer is None:
            continue
        if buyer.first_name is None:
            buyer.first_name = ""
        if buyer.last_name is None:
            buyer.last_name = ""
        if buyer.username is None:
            buyer.username = buyer.first_name + " " + buyer.last_name
        else:
            buyer.username = "@" + buyer.username
        await context.bot.send_message(
            update.message.from_user.id,
            f'Feedback inviato da {buyer.username} in data {feedback.date.date()}:\n\n"{feedback.contents}"',
            reply_markup=ReplyKeyboardRemove(),
        )

    total_feedback_count = len(feedbacks)
    await context.bot.send_message(
        update.message.from_user.id,
        f"L'utente @{seller.username} ha {total_feedback_count} feedback in totale, eccone alcuni 👆👆",
        reply_markup=ReplyKeyboardRemove(),
    )
