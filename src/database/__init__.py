from datetime import datetime

from src.config import get_default_post_datetime

from .cache import (
    CACHE,
    RolesEntry,
    get_id_from_username_cache,
    get_user_from_cache,
    insert_into_roles_cache,
    insert_into_username_cache,
    insert_into_users_cache,
    remove_role_from_roles_cache,
)
from .models.role import Role, get_roles_for_user
from .models.user import User


def get_user(id: int | None = None, username: str | None = None) -> User | None:
    from .models.user import get_user_from_id, get_user_from_username

    user: User | None
    if id is not None:
        user = get_user_from_cache(id=id)
        if user is not None:
            return user
        else:
            user = get_user_from_id(id=id)
            if user is not None:
                insert_into_users_cache(id=id, user=user)

            return user

    elif username is not None:
        id = get_id_from_username_cache(username=username)
        if id is not None:
            user: User = get_user_from_cache(id=id)
            if user is not None:
                return user

        user = get_user_from_username(username=username)
        if user is not None:
            insert_into_username_cache(username=user.username, id=user.id)
            insert_into_users_cache(id=id, user=user)

            return user


def update_user_info(
    id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> None:
    from .models.user import get_user_from_id, update_user_info_into_db

    update_user_info_into_db(
        id=id, username=username, first_name=first_name, last_name=last_name
    )

    user = get_user_from_id(id=id)
    insert_into_users_cache(id=id, user=user)
    insert_into_username_cache(username=username, id=id)


def update_user_post_dates(
    id: int,
    last_buy_post: datetime | None = None,
    last_sell_post: datetime | None = None,
) -> None:
    from .models.user import update_user_dates

    user: User = get_user(id=id)
    if user is None:
        return

    if last_buy_post is None:
        last_buy_post = user.last_buy_post
    if last_sell_post is None:
        last_sell_post = user.last_sell_post

    update_user_dates(
        id=user.id, last_buy_post=last_buy_post, last_sell_post=last_sell_post
    )
    user.last_buy_post = last_buy_post
    user.last_sell_post = last_sell_post
    insert_into_users_cache(id=id, user=user)


def reset_user_buy_post(id: int) -> None:
    from .models.user import update_user_dates

    user: User = get_user(id=id)
    if user is None:
        return

    update_user_dates(
        id=id,
        last_buy_post=get_default_post_datetime(),
        last_sell_post=user.last_sell_post,
    )
    user.last_buy_post = get_default_post_datetime()
    insert_into_users_cache(id=id, user=user)


def reset_user_sell_post(id: int) -> None:
    from .models.user import update_user_dates

    user: User = get_user(id=id)
    if user is None:
        return

    update_user_dates(
        id=id,
        last_buy_post=user.last_buy_post,
        last_sell_post=get_default_post_datetime(),
    )
    user.last_sell_post = get_default_post_datetime()
    insert_into_users_cache(id=id, user=user)


def add_role_to_user(id: int, role_name: Role) -> None:
    from .models.role import make_role

    make_role(user_id=id, role_name=role_name)
    insert_into_roles_cache(id=id, role_name=role_name)


def remove_role_from_user(id: int, role_name: Role) -> None:
    from .models.role import remove_role

    remove_role(user_id=id, role_name=role_name)
    remove_role_from_roles_cache(id=id, role_name=role_name)


def has_role(user_id: int, role_name: Role) -> bool:
    roles_entry: RolesEntry = CACHE.cached_roles.get(user_id)
    if roles_entry is not None:
        if role_name in roles_entry.roles:
            return True

    roles = get_roles_for_user(user_id=user_id)
    for role in roles:
        insert_into_roles_cache(id=user_id, role_name=role)

    if role_name in roles:
        return True
    else:
        return False
