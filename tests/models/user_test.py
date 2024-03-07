import unittest
from datetime import datetime

from src.config import get_default_post_datetime
from src.database.models.user import (
    get_user_from_id,
    update_user_dates,
    update_user_info_into_db,
)
from tests.test_data import (
    clean_test_database,
    mock_users,
    reset_users,
    start_test_database,
)


class UserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        start_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clean_test_database()

    def test_user_class(self):
        user = get_user_from_id(1)
        self.assertEqual(mock_users[0], user)
        self.assertEqual(user.last_buy_post, get_default_post_datetime())
        self.assertEqual(user.last_sell_post, get_default_post_datetime())

        user = get_user_from_id(2)
        self.assertEqual(mock_users[1], user)
        self.assertEqual(user.last_buy_post, get_default_post_datetime())
        self.assertEqual(user.last_sell_post, get_default_post_datetime())

        user = get_user_from_id(10)
        self.assertEqual(user, None)

    def test_set_date(self):
        update_user_dates(
            1, datetime(year=2022, month=6, day=2), datetime(year=2021, month=1, day=12)
        )
        user = get_user_from_id(1)
        self.assertEqual(user.last_buy_post, datetime(year=2022, month=6, day=2))
        self.assertEqual(user.last_sell_post, datetime(year=2021, month=1, day=12))

        update_user_dates(1, get_default_post_datetime(), get_default_post_datetime())
        user = get_user_from_id(1)
        self.assertEqual(user.last_buy_post, get_default_post_datetime())
        self.assertEqual(user.last_sell_post, get_default_post_datetime())

        reset_users()

    def test_update_user(self):
        update_user_info_into_db(
            1,
            username="newusername",
            first_name=mock_users[0].first_name,
            last_name=mock_users[0].last_name,
        )
        user = get_user_from_id(1)
        self.assertEqual(user.username, "newusername")
        self.assertEqual(user.first_name, mock_users[0].first_name)
        self.assertEqual(user.last_name, mock_users[0].last_name)

        update_user_info_into_db(
            2,
            username=mock_users[1].username,
            first_name="update",
            last_name="updatelastname",
        )
        user = get_user_from_id(2)
        self.assertEqual(user.username, mock_users[1].username)
        self.assertEqual(user.first_name, "update")
        self.assertEqual(user.last_name, "updatelastname")

        reset_users()
