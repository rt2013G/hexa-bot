from dataclasses import dataclass
from telegram.ext import Application
from src.jobs import clean_cache_job, post_logs_job

@dataclass
class BotParameters:
    token: str
    handlers: dict

class Bot:
    def __init__(self, parameters: BotParameters) -> None:
        self.application = Application.builder().token(parameters.token).build()
        self.add_handlers(parameters.handlers)
        self.job_queue = self.application.job_queue
        self.add_jobs()

    def add_handlers(self, handlers) -> None:
        self.application.add_handlers(handlers=handlers)

    def add_jobs(self) -> None:
        self.job_queue.run_repeating(clean_cache_job, interval=300, first=300)
        self.job_queue.run_repeating(post_logs_job, interval=60, first=30)

    def run(self) -> None:
        self.application.run_polling(drop_pending_updates=True)
        