import os
import sys

from dotenv import load_dotenv
from telegram import LinkPreviewOptions
from telegram.ext import Defaults

from app import Bot, BotParameters
from app.database.models.base import create_database
from app.handlers import handlers
from app.logger import set_up_logger
from app.utils import load_card_name_db


def main() -> None:
    if len(sys.argv) > 2:
        print("error. usage: python hexa_bot.py <mode>")
        sys.exit(0)

    load_dotenv()
    set_up_logger()
    create_database()
    load_card_name_db()

    bot_token = os.getenv("BOT_TOKEN")
    if bot_token is None:
        print("error. bot token environment variable was not set")
        sys.exit(0)

    params = BotParameters(
        token=bot_token,
        handlers=handlers,
        defaults=Defaults(link_preview_options=LinkPreviewOptions(is_disabled=True)),
    )
    bot = Bot(parameters=params)
    mode = "webhook" if len(sys.argv) == 2 and sys.argv[1] == "webhook" else "polling"
    bot.run(mode=mode)


if __name__ == "__main__":
    main()
