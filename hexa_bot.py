import os
import sys

from dotenv import load_dotenv
from telegram import LinkPreviewOptions
from telegram.ext import Defaults

from src import config as cfg
from src.components import Bot, BotParameters
from src.database.cache import init_cache
from src.database.models.base import init_db
from src.handlers.admin_handlers import get_admin_handlers
from src.handlers.command_handlers import get_command_handlers
from src.handlers.market_handlers import get_market_handlers
from src.handlers.seller_auth import get_auth_conv_handler
from src.handlers.service_handlers import get_service_handlers
from src.utils.logger import set_up_logger


def main() -> None:
    if not len(sys.argv) == 2:
        print("error. usage: python hexa_bot.py <mode>")
        sys.exit(0)

    load_dotenv()
    cfg.GLOBAL_CONFIGS = cfg.load_configs()

    set_up_logger()
    init_db(roles=cfg.get_roles())
    init_cache()

    bot_token = (
        os.getenv("BOT_TOKEN")
        if sys.argv[1] == "deploy"
        else os.getenv("BOT_TOKEN_DEBUG")
    )
    if bot_token is None:
        print("error. bot token env variable is not set")
        sys.exit(0)
    params = BotParameters(
        token=bot_token,
        handlers={
            0: get_service_handlers(),
            1: get_admin_handlers(),
            2: get_command_handlers(),
            3: get_market_handlers(),
            4: get_auth_conv_handler(),
        },
        defaults=Defaults(link_preview_options=LinkPreviewOptions(is_disabled=True)),
    )
    bot = Bot(parameters=params)
    bot.run()


if __name__ == "__main__":
    main()
