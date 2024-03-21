from .info import info_handlers
from .market import market_handlers

user_commands_handlers: list = market_handlers() + info_handlers()
