import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from telegram.ext import ContextTypes

from .models.role import Role
from .models.user import User


@dataclass
class UserEntry:
    user: User
    time: datetime


@dataclass
class IdEntry:
    id: int
    time: datetime


@dataclass
class RolesEntry:
    roles: list[Role]
    time: datetime


@dataclass
class Cache:
    cached_users: dict[int, UserEntry]
    cached_usernames_to_id: dict[str, IdEntry]
    cached_roles: dict[int, RolesEntry]


CACHE: Cache = Cache(cached_users={}, cached_usernames_to_id={}, cached_roles={})


def insert_into_users_cache(id: int, user: User) -> None:
    CACHE.cached_users[id] = UserEntry(user=user, time=datetime.now())


def insert_into_username_cache(username: str, id: int) -> None:
    CACHE.cached_usernames_to_id[username] = IdEntry(id=id, time=datetime.now())


def insert_into_roles_cache(id: int, role_name: Role) -> None:
    value: RolesEntry = CACHE.cached_roles.get(id)
    if value is None:
        CACHE.cached_roles[id] = RolesEntry(roles=[role_name], time=datetime.now())
    elif role_name not in CACHE.cached_roles[id].roles:
        CACHE.cached_roles[id].roles.append(role_name)
        CACHE.cached_roles[id].time = datetime.now()


def remove_role_from_roles_cache(id: int, role_name: Role) -> None:
    value: RolesEntry = CACHE.cached_roles.get(id)
    if value is None:
        return
    elif role_name not in CACHE.cached_roles[id].roles:
        return
    else:
        CACHE.cached_roles[id].roles.remove(role_name)


def get_user_from_cache(id: int) -> User | None:
    user_entry: UserEntry = CACHE.cached_users.get(id)
    if user_entry is None:
        return None
    else:
        return user_entry.user


def get_id_from_username_cache(username: str) -> int | None:
    id_entry: IdEntry = CACHE.cached_usernames_to_id.get(username)
    if id_entry is None:
        return None
    else:
        return id_entry.id


async def clean_users_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for user_id in list(CACHE.cached_users):
        if CACHE.cached_users[user_id].time < datetime.now() - timedelta(hours=1):
            del CACHE.cached_users[user_id]

    logging.log(logging.INFO, "Users cache cleaned.")


async def clean_roles_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for username in list(CACHE.cached_usernames_to_id):
        if CACHE.cached_usernames_to_id[username].time < datetime.now() - timedelta(
            days=2
        ):
            del CACHE.cached_usernames_to_id[username]

    for user_id in list(CACHE.cached_roles):
        if CACHE.cached_roles[user_id].time < datetime.now() - timedelta(days=1):
            del CACHE.cached_roles[user_id]

    logging.log(logging.INFO, "Roles and username caches cleaned.")
