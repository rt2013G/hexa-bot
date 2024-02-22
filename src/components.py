from dataclasses import dataclass
from telegram.ext import Application
from telegram.ext import (
    CommandHandler,
    filters
)
import src.handlers as h

@dataclass
class BotParameters:
    token: str

class Bot:
    def __init__(self, parameters: BotParameters) -> None:
        self.application = Application.builder().token(parameters.token).build()
        self.__add_handlers()

    def __add_handlers(self) -> None:
        self.application.add_handler(CommandHandler("start", h.start, filters=filters.ChatType.PRIVATE))

    def run(self) -> None:
        self.application.run_polling(drop_pending_updates=True)