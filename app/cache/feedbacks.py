from dataclasses import dataclass
from datetime import datetime

from app import database as db


@dataclass
class SellerEntry:
    feedbacks: list[db.Feedback]
    time: datetime


@dataclass
class FeedbacksCache:
    sellers: dict[int, SellerEntry]


feedbacks_cache = FeedbacksCache(sellers={})


def insert_feedback(
    seller_id: int, buyer_id: int, contents: str, date: datetime
) -> None:
    db.insert_feedback(
        seller_id=seller_id, buyer_id=buyer_id, contents=contents, date=date
    )
    if feedbacks_cache.sellers.get(seller_id):
        del feedbacks_cache.sellers[seller_id]


def get_feedbacks(seller_id: int) -> list[db.Feedback]:
    if seller_entry := feedbacks_cache.sellers.get(seller_id):
        return seller_entry.feedbacks

    feedbacks = db.get_feedbacks(seller_id=seller_id)
    feedbacks_cache[seller_id] = SellerEntry(feedbacks=feedbacks, time=datetime.now())
    return feedbacks
