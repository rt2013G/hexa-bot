import os
import sys

from dotenv import load_dotenv
from telegram import LinkPreviewOptions
from telegram.ext import Defaults

from src import config as cfg
from src.components import Bot, BotParameters
from src.database.models.base import create_database
from src.handlers import handlers
from src.logger import set_up_logger


def main() -> None:
    if not len(sys.argv) == 2:
        print("error. usage: python hexa_bot.py <mode>")
        sys.exit(0)

    load_dotenv()
    cfg.GLOBAL_CONFIGS = cfg.load_configs()

    set_up_logger()
    create_database(roles=cfg.get_roles())

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
        handlers=handlers,
        defaults=Defaults(link_preview_options=LinkPreviewOptions(is_disabled=True)),
    )
    bot = Bot(parameters=params)
    bot.run()


if __name__ == "__main__":
    main()
