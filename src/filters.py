from telegram import Message
from telegram.ext.filters import MessageFilter

from src.config import get_approval_id, get_debug_user_id, get_main_id, get_market_id
from src.utils.utils import is_feedback_post, is_role


class AdminFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return is_role(message.from_user.id, "admin")


class MarketGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.chat.id == get_market_id() else False


class MainGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.chat.id == get_main_id() else False


class ApprovalGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.chat.id == get_approval_id() else False


class DebugUserFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.from_user.id == get_debug_user_id() else False


class MediaGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.media_group_id is not None else False


class FeedbackFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        text: str
        try:
            text = message.text
        except AttributeError:
            return False
        return is_feedback_post(text=text)
