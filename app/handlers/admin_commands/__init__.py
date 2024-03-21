from .helpers import helpers_handlers
from .market import market_handlers
from .roles import role_handlers

admin_commands_handlers: list = role_handlers() + helpers_handlers() + market_handlers()
