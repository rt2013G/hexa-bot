from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from telegram import (
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    Update,
)
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.helpers import effective_message_type

from src.config import get_feedback_channel_id
from src.database.dbms import get_user_from_id, insert_feedback, update_user_dates
from src.filters import (
    AdminFilter,
    FeedbackFilter,
    MainGroupFilter,
    MarketGroupFilter,
    MediaGroupFilter,
)
from src.utils.utils import (
    get_user_from_text,
    has_sent_buy_post_today,
    has_sent_sell_post_today,
    is_buy_post,
    is_role,
    is_sell_post,
)


def get_chat_handlers() -> list:
    return [
        MessageHandler(
            ~filters.COMMAND & MainGroupFilter() & ~AdminFilter(), main_msg_handler
        ),
        MessageHandler(
            ~filters.COMMAND
            & MarketGroupFilter()
            & MediaGroupFilter()
            & ~AdminFilter(),
            market_media_group_handler,
        ),
        MessageHandler(
            ~filters.COMMAND
            & MarketGroupFilter()
            & ~MediaGroupFilter()
            & ~FeedbackFilter()
            & ~AdminFilter(),
            market_post_handler,
        ),
        MessageHandler(
            ~filters.COMMAND
            & MarketGroupFilter()
            & ~MediaGroupFilter()
            & FeedbackFilter(),
            feedback_msg_handler,
        ),
    ]


async def main_msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


@dataclass
class MediaGroupMediaData:
    media_type: str
    media_id: str
    caption: str
    media_msg: Message


MEDIA_GROUP_TYPES = {
    "document": InputMediaDocument,
    "photo": InputMediaPhoto,
    "video": InputMediaVideo,
}


async def market_media_group_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.message
    media_type = effective_message_type(message)
    media_id = (
        message.photo[-1].file_id
        if message.photo
        else message.effective_attachment.file_id
    )
    media_data = MediaGroupMediaData(
        media_type=media_type,
        media_id=media_id,
        caption=message.caption_html,
        media_msg=update.message,
    )
    jobs = context.job_queue.get_jobs_by_name(str(message.media_group_id))
    if jobs:
        jobs[0].data.append(media_data)
    else:
        context.job_queue.run_once(
            callback=media_group_job,
            when=1,
            data=[media_data],
            name=str(message.media_group_id),
        )


async def media_group_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    media_group: list = []
    data: list[MediaGroupMediaData] = context.job.data
    post_type: Literal["buy", "sell", "invalid"]
    user = get_user_from_id(data[-1].media_msg.from_user.id)
    if user is None:
        for media in data:
            await media.media_msg.delete()
        return

    for media in data:
        if media.caption is not None:
            if is_buy_post(media.caption):
                post_type = "buy"
            elif is_sell_post(media.caption) and is_role(user.id, "seller"):
                post_type = "sell"

        media_group.append(
            MEDIA_GROUP_TYPES[media.media_type](
                media=media.media_id, caption=media.caption
            )
        )

    if post_type == "buy":
        if has_sent_buy_post_today(user.id):
            post_type = "invalid"
            await context.bot.send_message(
                user.id,
                "Il tuo messaggio è stato eliminato, hai già inviato un post di cerco oggi!",
            )
        else:
            update_user_dates(user.id, datetime.now(), user.last_sell_post)
    elif post_type == "sell":
        if has_sent_sell_post_today(user.id):
            post_type = "invalid"
            await context.bot.send_message(
                user.id,
                "Il tuo messaggio è stato eliminato, hai già inviato un post di vendo oggi!",
            )
        else:
            update_user_dates(user.id, user.last_buy_post, datetime.now())

    if post_type == "invalid":
        for media in data:
            await media.media_msg.delete()


async def market_post_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    msg: str
    if update.message.text is not None:
        msg = update.message.text
    elif update.message.caption is not None:
        msg = update.message.caption
    else:
        await update.message.delete()
        return

    user = get_user_from_id(update.message.from_user.id)
    if user is None:
        await update.message.delete()
        return
    if is_buy_post(msg):
        if has_sent_buy_post_today(user.id):
            await context.bot.send_message(
                user.id,
                "Il tuo messaggio è stato eliminato, hai già inviato un post di cerco oggi!",
            )
            await update.message.delete()
        else:
            update_user_dates(user.id, datetime.now(), user.last_sell_post)

    elif (
        is_sell_post(msg)
        and (update.message.photo or update.message.video or update.message.video_note)
        and is_role(update.message.from_user.id, "seller")
    ):
        if has_sent_sell_post_today(user.id):
            await context.bot.send_message(
                user.id,
                "Il tuo messaggio è stato eliminato, hai già inviato un post di vendo oggi!",
            )
            await update.message.delete()
        else:
            update_user_dates(user.id, user.last_buy_post, datetime.now())
    else:
        await update.message.delete()


async def feedback_msg_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = get_user_from_id(update.message.from_user.id)
    if user is None:
        await update.message.delete()
        return
    msg = update.message.text
    seller = get_user_from_text(msg)
    if seller is None:
        await context.bot.send_message(
            user.id,
            "Il tuo feedback non è stato inserito! Assicurati di aver scritto correttamente lo @username del venditore.",
        )
        await update.message.delete()
        return
    if user.id == seller.id:
        await context.bot.send_message(
            user.id,
            "Non puoi aggiungere un feedback a te stesso!",
        )
        await update.message.delete()
        return

    if not is_role(seller.id, "seller"):
        await context.bot.send_message(
            user.id,
            "Il tuo feedback non è stato inserito! L'utente da cui hai acquistato non è un venditore!",
        )
        await update.message.delete()
        return

    insert_feedback(
        seller_id=seller.id, buyer_id=user.id, contents=msg, date=datetime.now()
    )
    await context.bot.send_message(
        user.id,
        f"Il tuo feedback per @{seller.username} è stato inserito correttamente.",
    )
    await context.bot.forward_message(
        chat_id=get_feedback_channel_id(),
        from_chat_id=update.message.chat_id,
        message_id=update.message.id,
    )
