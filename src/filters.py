from telegram import Message
from telegram.ext.filters import MessageFilter
from src import utils

class AdminFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return utils.is_admin(message.from_user.id)
    
class MarketGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return utils.is_market_group(message.chat.id)
    
class MainGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return utils.is_main_group(message.chat.id)
    
class ApprovalGroupFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return utils.is_approval_group(message.chat.id)

