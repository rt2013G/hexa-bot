from dataclasses import dataclass
from datetime import datetime

from app.database.models.feedback import Feedback


@dataclass
class FeedbackListEntry:
    feedbacks: list[Feedback]
    time: datetime


@dataclass
class FeedbacksCache:
    feedbacks_entries: dict[int, FeedbackListEntry]


feedbacks_cache = FeedbacksCache(feedbacks_entries={})


def insert_feedback(
    seller_id: int, buyer_id: int, contents: str, date: datetime
) -> None:
    pass


def get_feedbacks(seller_id: int, start: int = 0, end: int = 99999) -> list[Feedback]:
    pass
