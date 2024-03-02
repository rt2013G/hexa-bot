import os
import sys

from dotenv import load_dotenv

from src import config
from src.cache import init_cache
from src.components import Bot, BotParameters
from src.database.dbms import init_db
from src.handlers import admin_handlers as ah
from src.handlers import chat_handlers as chh
from src.handlers import command_handlers as ch
from src.utils.logger import set_up_logger


def main() -> None:
    if not len(sys.argv) == 2:
        print("error. usage: python hexa_bot.py <mode>")
        sys.exit(0)
    load_dotenv()
    config.GLOBAL_CONFIGS = config.load_configs()

    set_up_logger()

    init_db()
    init_cache()

    bot_token = (
        os.getenv("BOT_TOKEN")
        if sys.argv[1] == "deploy"
        else os.getenv("BOT_TOKEN_DEBUG")
    )
    if bot_token is None:
        print("error. bot token env variabile is not set")
        sys.exit(0)
    params = BotParameters(
        token=bot_token,
        handlers={
            0: ch.get_command_handlers(),
            1: ah.get_admin_handlers(),
            2: chh.get_chat_handlers(),
        },
    )
    bot = Bot(parameters=params)
    bot.run()


if __name__ == "__main__":
    main()
