from .roles import get_role_handlers
from .utils import get_utils_handlers

admin_commands_handlers: list = get_role_handlers() + get_utils_handlers()
