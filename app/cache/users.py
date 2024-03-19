from dataclasses import dataclass
from datetime import datetime

from app.database.models.role import Role
from app.database.models.user import User


@dataclass
class UserEntry:
    user: User
    time: datetime


@dataclass
class UserIdEntry:
    id: int
    time: datetime


@dataclass
class UserRolesEntry:
    roles: set[Role]
    time: datetime


@dataclass
class UsersCache:
    users: dict[int, UserEntry]
    ids: dict[str, UserIdEntry]
    roles: dict[int, UserRolesEntry]


users_cache = UsersCache(users={}, ids={}, roles={})


def insert_user(
    id: int, username: str | None, first_name: str | None, last_name: str | None
) -> None:
    pass


def get_user(id: int | None = None, username: str | None = None) -> User | None:
    pass


def update_user_info(
    id: int, username: str | None, first_name: str | None, last_name: str | None
) -> None:
    pass


def update_user_date(
    id: int,
    last_buy_post: datetime | None,
    last_sell_post: datetime | None,
) -> None:
    pass


def insert_id(username: str) -> None:
    pass


def insert_role(id: int, role: Role) -> None:
    pass


def remove_role(id: int, role: Role) -> None:
    pass


def has_role(id: int, role: Role) -> bool:
    pass
