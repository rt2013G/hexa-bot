import sys
import os
from src.components import Bot, BotParameters
from dotenv import load_dotenv


def main():
    if not len(sys.argv) == 2:
        print("error. usage: python hexa_bot.py <mode>")
        sys.exit(0)
    load_dotenv()
    params = BotParameters(
        token=os.getenv("BOT_TOKEN") if sys.argv[1] == "deploy" else os.getenv("BOT_TOKEN_DEBUG")
    )
    bot = Bot(parameters=params)
    bot.run()

if __name__ == "__main__":
    main()