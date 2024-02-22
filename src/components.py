from dataclasses import dataclass
from telegram.ext import Application

@dataclass
class BotParameters:
    token: str
    handlers: dict

class Bot:
    def __init__(self, parameters: BotParameters) -> None:
        self.__application = Application.builder().token(parameters.token).build()
        self.__add_handlers(parameters.handlers)

    def __add_handlers(self, handlers) -> None:
        self.__application.add_handlers(handlers=handlers)

    def run(self) -> None:
        self.__application.run_polling(drop_pending_updates=True)