from telegram import Message
from telegram.ext.filters import MessageFilter
from src.utils.utils import is_admin, is_market_group, is_main_group, is_approval_group

class AdminFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return is_admin(message.from_user.id)
    
class MarketGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return is_market_group(message.chat.id)
    
class MainGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return is_main_group(message.chat.id)
    
class ApprovalGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return is_approval_group(message.chat.id)

