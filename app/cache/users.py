from dataclasses import dataclass
from datetime import datetime

from app import database as db
from app.constants import Dates


@dataclass
class UserEntry:
    user: db.User
    time: datetime


@dataclass
class UserRolesEntry:
    roles: set[db.Role]
    time: datetime


@dataclass
class UsersCache:
    users: dict[int, UserEntry]
    ids: dict[str, int]
    roles: dict[int, UserRolesEntry]


users_cache = UsersCache(users={}, ids={}, roles={})


def insert_user(
    id: int, username: str | None, first_name: str | None, last_name: str | None
) -> None:
    db.insert_user(id=id, username=username, first_name=first_name, last_name=last_name)
    users_cache.users[id] = UserEntry(
        user=db.User(
            (
                id,
                username,
                first_name,
                last_name,
                Dates.MARKET_EPOCH,
                Dates.MARKET_EPOCH,
            )
        ),
        time=datetime.now(),
    )
    users_cache.ids[username] = id


def get_user(id: int | None = None, username: str | None = None) -> db.User | None:
    if id:
        if user_entry := users_cache.users.get(id):
            return user_entry.user
        elif user := db.get_user_from_id(id=id):
            users_cache.users[id] = UserEntry(user=user, time=datetime.now())
            return user

    elif username:
        if id := users_cache.ids.get(username):
            if user_entry := users_cache.users.get(id):
                return user_entry.user
            user = db.get_user_from_id(id=id)
            if user:
                users_cache.users[id] = UserEntry(user=user, time=datetime.now())

            return user
        elif user := db.get_user_from_username(username=username):
            users_cache.ids[username] = user.id
            users_cache.users[user.id] = UserEntry(user=user, time=datetime.now())
            return user


def update_user_info(
    id: int, username: str | None, first_name: str | None, last_name: str | None
) -> None:
    db.update_user_info(
        id=id, username=username, first_name=first_name, last_name=last_name
    )
    users_cache.ids[username] = id
    users_cache.users[id].user.username = username
    users_cache.users[id].user.first_name = first_name
    users_cache.users[id].user.last_name = last_name


def update_user_date(
    id: int,
    last_buy_post: datetime | None = None,
    last_sell_post: datetime | None = None,
) -> None:
    if last_buy_post:
        db.update_user_last_buy_post(id=id, last_buy_post=last_buy_post)
        if users_cache.users.get(id):
            users_cache.users[id].user.last_buy_post = last_buy_post

    if last_sell_post:
        db.update_user_last_sell_post(id=id, last_sell_post=last_sell_post)
        if users_cache.users.get(id):
            users_cache.users[id].user.last_sell_post = last_sell_post


def insert_role(id: int, role_name: db.Role) -> None:
    db.insert_role(user_id=id, role_name=role_name)
    if users_cache.roles.get(id):
        users_cache.roles[id].roles.add(role_name)
        users_cache.roles[id].time = datetime.now()
    else:
        users_cache.roles[id] = UserRolesEntry(
            roles=set(role_name), time=datetime.now()
        )


def remove_role(id: int, role_name: db.Role) -> None:
    db.remove_role(user_id=id, role_name=role_name)
    if roles_entry := users_cache.roles.get(id):
        if role_name in roles_entry.roles:
            users_cache.roles[id].roles.remove(role_name)


def has_role(id: int, role_name: db.Role) -> bool:
    if roles_entry := users_cache.roles.get(id):
        if role_name in roles_entry.roles:
            return True
        else:
            return False

    roles = db.get_roles(user_id=id)
    users_cache.roles[id] = UserRolesEntry(roles=roles, time=datetime.now())
    return True if role_name in roles else False
