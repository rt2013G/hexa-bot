from telegram import Message
from telegram.ext.filters import MessageFilter

from app.cache import has_role
from app.config import approval_id, debug_user_id, main_id, market_id
from app.constants import Roles
from app.message_helpers import is_feedback_post


class AdminFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return has_role(message.from_user.id, Roles.ADMIN)


class ModeratorFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return has_role(message.from_user.id, Roles.MODERATOR)


class MarketGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.chat.id == market_id() else False


class MainGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.chat.id == main_id() else False


class ApprovalGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.chat.id == approval_id() else False


class DebugUserFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return True if message.from_user.id == debug_user_id() else False


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
        if text is None:
            return False
        return is_feedback_post(text=text)
