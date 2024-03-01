from dataclasses import dataclass
from datetime import datetime
from src.database.model import User
from src.utils.utils import is_role

@dataclass
class UserCacheEntry:
    username: str
    is_seller: bool
    time: datetime

USERS_CACHE: dict

def init_cache() -> None:
    global USERS_CACHE
    USERS_CACHE = {}

def insert_into_cache(user: User,
                      is_seller = None,
                      time = datetime.now()) -> None:
    if is_seller is None:
        is_seller = is_role(user.id, "seller")
    entry = UserCacheEntry(
        username=user.username,
        is_seller=is_seller,
        time=time
    )
    USERS_CACHE[user.id] = entry