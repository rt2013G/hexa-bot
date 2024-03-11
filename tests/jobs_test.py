import unittest

from telegram.ext import ContextTypes

from app.config import get_default_post_datetime
from app.database.cache import (
    CACHE,
    clean_users_cache_job,
    get_user_from_cache,
    insert_into_users_cache,
)
from tests.test_data import mock_users


class JobsTest(unittest.IsolatedAsyncioTestCase):
    async def test_clean_cache_job(self) -> None:
        insert_into_users_cache(id=mock_users[0].id, user=mock_users[0])
        user = get_user_from_cache(mock_users[0].id)
        self.assertEqual(user, mock_users[0])

        insert_into_users_cache(id=mock_users[1].id, user=mock_users[1])
        user = get_user_from_cache(mock_users[1].id)
        self.assertEqual(user, mock_users[1])

        for key in CACHE.cached_users:
            CACHE.cached_users[key].time = get_default_post_datetime()
        await clean_users_cache_job(context=ContextTypes.DEFAULT_TYPE)
        self.assertEqual(len(CACHE.cached_users), 0)
