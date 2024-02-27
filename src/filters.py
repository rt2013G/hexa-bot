from telegram import Message
from telegram.ext.filters import MessageFilter
from src.utils.utils import is_role
from src.config import get_main_id, get_market_id, get_approval_id, get_debug_user_id

class AdminFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return is_role(message.from_user.id, "admin")
    
class MarketGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.chat.id == get_market_id()
    
class MainGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.chat.id == get_main_id()
    
class ApprovalGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.chat.id == get_approval_id()

class DebugUserFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.from_user.id == get_debug_user_id()
    
class AnnounceFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return is_role(message.from_user.id, "announce")
    