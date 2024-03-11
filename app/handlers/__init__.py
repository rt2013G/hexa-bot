from .admin_handlers import get_admin_handlers
from .announce_handlers import get_announce_handlers
from .command_handlers import get_command_handlers
from .guess_game_handlers import get_guess_game_conv_handler
from .market_handlers import get_market_handlers
from .seller_auth import get_auth_conv_handler
from .service_handlers import get_service_handlers

handlers = {
    0: get_service_handlers(),
    1: get_admin_handlers(),
    2: get_command_handlers(),
    3: get_market_handlers(),
    4: get_auth_conv_handler(),
    5: get_guess_game_conv_handler(),
    6: get_announce_handlers(),
}
