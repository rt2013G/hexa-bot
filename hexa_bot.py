import os
import sys

from dotenv import load_dotenv
from telegram import LinkPreviewOptions
from telegram.ext import Defaults

from app import Bot, BotParameters
from app.database import create_database
from app.handlers import handlers
from app.logger import set_up_logger


def main() -> None:
    if len(sys.argv) > 3:
        print("error. usage: python hexa_bot.py [webhook] [debug]")
        sys.exit(0)

    load_dotenv(override=True)

    if len(sys.argv) == 2 and sys.argv[1] == "migrate":
        from migrations import upgrade

        upgrade()
        print("Migration completed.")
        sys.exit(0)

    set_up_logger()
    create_database()

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
    mode = "webhook" if len(sys.argv) >= 2 and sys.argv[1] == "webhook" else "polling"
    bot.run(
        mode=mode,
        webhook_secret=os.getenv("WEBHOOK_SECRET"),
        webhook_url=os.getenv("WEBHOOK_URL"),
    )


if __name__ == "__main__":
    main()
