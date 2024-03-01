from dataclasses import dataclass
from datetime import datetime

from src.database.model import User


@dataclass
class UserCacheEntry:
    user: User
    is_seller: bool
    time: datetime


USERS_CACHE: dict[int, UserCacheEntry]
ADMIN_CACHE: list[int]


def init_cache() -> None:
    global USERS_CACHE
    USERS_CACHE = {}
    global ADMIN_CACHE
    ADMIN_CACHE = []


def insert_into_cache(user: User, is_seller: bool, time: datetime) -> None:
    entry = UserCacheEntry(user=user, is_seller=is_seller, time=time)
    USERS_CACHE[user.id] = entry
