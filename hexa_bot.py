import sys
import os
from src.components import Bot, BotParameters
from dotenv import load_dotenv
from src.handlers import (
    command_handlers as ch,
    admin_handlers as ah,
    market_handlers as mkh,
    main_handlers as mh,
)


def main():
    if not len(sys.argv) == 2:
        print("error. usage: python hexa_bot.py <mode>")
        sys.exit(0)
    load_dotenv()
    params = BotParameters(
        token=os.getenv("BOT_TOKEN") if sys.argv[1] == "deploy" else os.getenv("BOT_TOKEN_DEBUG"),
        handlers={
            0: ch.get_command_handlers(),
            1: ah.get_admin_handlers(),
            2: mkh.get_market_handlers(),
            3: mh.get_main_handlers(),
        }
    )
    bot = Bot(parameters=params)
    bot.run()

if __name__ == "__main__":
    main()