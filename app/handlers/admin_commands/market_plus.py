import random
from datetime import datetime, timedelta

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, filters

from app.config import get_market_id, get_market_plus_id
from app.database import (MarketPlusPost, get_posts_to_delete,
                          get_posts_to_send, insert_market_plus_post,
                          update_delete_market_plus_post, update_posted_date)
from app.filters import AdminFilter


def market_plus_handlers() -> list[CommandHandler]:
    return [
        CommandHandler(
            "marketplus", market_plus_handler, filters.ChatType.PRIVATE & AdminFilter()
        )
    ]


async def market_plus_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return

    if (
        update.message.reply_to_message is None
        or update.message.reply_to_message.from_user.id != update.message.from_user.id
    ):
        await context.bot.send_message(
            update.message.from_user.id,
            "Per inviare un messaggio nel market plus, scrivi prima il messaggio, dopodiché rispondi ad esso con /marketplus <durata in ore>.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await context.bot.send_message(
            update.message.from_user.id,
            "Per inviare un messaggio nel market plus, scrivi prima il messaggio, dopodiché rispondi ad esso con /marketplus <durata in ore>.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    forwarded_message = await update.message.reply_to_message.forward(
        chat_id=get_market_plus_id()
    )
    end_date = datetime.now() + timedelta(hours=int(context.args[0]))
    insert_market_plus_post(message_id=forwarded_message.id, end_date=end_date)
    await context.bot.send_message(
        update.message.from_user.id,
        "Messaggio market plus inviato correttamente!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def market_plus_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    if datetime.now().hour < 8:
        context.job.schedule_removal()
        context.job_queue.run_repeating(
            callback=market_plus_job,
            interval=1800,
            first=25200,
        )

    posts: list[MarketPlusPost] = get_posts_to_send()
    if len(posts) == 0:
        return
    # trunk-ignore(bandit/B311)
    post_to_send: MarketPlusPost = random.choice(posts)
    if post_to_send.last_posted_market_id:
        await context.bot.delete_message(
            chat_id=get_market_id(), message_id=post_to_send.last_posted_market_id
        )
    forwarded_post = await context.bot.forward_message(
        chat_id=get_market_id(),
        from_chat_id=get_market_plus_id(),
        message_id=post_to_send.message_id,
    )
    await context.bot.pin_chat_message(
        get_market_id(), message_id=forwarded_post.id, disable_notification=False
    )
    update_posted_date(message_id=post_to_send.message_id, market_id=forwarded_post.id)

    posts_to_delete: list[MarketPlusPost] = get_posts_to_delete()
    for post in posts_to_delete:
        if post.message_id:
            await context.bot.delete_message(
                chat_id=get_market_plus_id(), message_id=post.message_id
            )
        if post.last_posted_market_id:
            await context.bot.delete_message(
                chat_id=get_market_id(), message_id=post.last_posted_market_id
            )
        update_delete_market_plus_post(post.message_id)
