import logging
import os
from dataclasses import dataclass
from typing import Literal

from telegram.ext import Application, Defaults

from app.card_search import clean_card_data_job
from app.database.cache import clean_roles_cache_job, clean_users_cache_job
from app.logger import post_logs_job


@dataclass
class BotParameters:
    token: str
    handlers: dict
    defaults: Defaults


class Bot:
    def __init__(self, parameters: BotParameters) -> None:
        self.application = (
            Application.builder()
            .token(parameters.token)
            .defaults(parameters.defaults)
            .build()
        )
        self.add_handlers(parameters.handlers)
        self.add_jobs()

    def add_handlers(self, handlers: dict[int, list]) -> None:
        self.application.add_handlers(handlers=handlers)

    def add_jobs(self) -> None:
        self.job_queue = self.application.job_queue
        self.job_queue.run_repeating(clean_users_cache_job, interval=300, first=300)
        self.job_queue.run_repeating(clean_roles_cache_job, interval=43200, first=43200)
        self.job_queue.run_repeating(post_logs_job, interval=60, first=60)
        self.job_queue.run_repeating(clean_card_data_job, interval=21600, first=21600)

    def run(
        self,
        mode: Literal["polling", "webhook"],
        webhook_secret: str | None = None,
        webhook_url: str | None = None,
    ) -> None:
        if mode == "polling":
            logging.log(logging.INFO, "Application started in polling mode...")
            self.application.run_polling(drop_pending_updates=True)
        elif mode == "webhook":
            logging.log(logging.INFO, "Application started in webhook mode...")
            self.application.run_webhook(
                # trunk-ignore(bandit/B104)
                listen="0.0.0.0",
                port=int(os.environ.get("PORT", "8443")),
                secret_token=webhook_secret,
                webhook_url=webhook_url,
                drop_pending_updates=True,
            )
