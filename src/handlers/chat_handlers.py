from dataclasses import dataclass

from telegram import (
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    Update,
)
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.helpers import effective_message_type

from src.filters import (
    AdminFilter,
    MainGroupFilter,
    MarketGroupFilter,
    MediaGroupFilter,
)
from src.utils.utils import is_buy_post, is_feedback_post, is_role, is_sell_post


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
            & ~AdminFilter(),
            market_post_handler,
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

    is_post_valid = False
    for media in data:
        if media.caption is not None:
            if is_buy_post(media.caption):
                # TODO check last buy post date here
                is_post_valid = True
            elif is_sell_post(media.caption) and is_role(
                media.media_msg.from_user.id, "seller"
            ):
                # TODO check last sell post date here
                is_post_valid = True

        media_group.append(
            MEDIA_GROUP_TYPES[media.media_type](
                media=media.media_id, caption=media.caption
            )
        )

    if is_post_valid:
        # update last buy or sell post dates accordingly
        pass
    else:
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

    is_post_valid = False
    if is_buy_post(msg):
        # TODO check last buy post date here
        is_post_valid = True
    elif (
        is_sell_post(msg)
        and (update.message.photo or update.message.video or update.message.video_note)
        and is_role(update.message.from_user.id, "seller")
    ):
        # TODO check last sell post date here
        is_post_valid = True
    elif is_feedback_post(msg) and not is_sell_post(msg):
        is_post_valid = True

    if not is_post_valid:
        await update.message.delete()
