import unittest
from datetime import datetime

from app.config import get_default_post_datetime
from app.database import (
    add_role_to_user,
    get_user,
    has_role,
    remove_role_from_user,
    reset_user_buy_post,
    reset_user_sell_post,
    update_user_info,
    update_user_post_dates,
)
from tests.test_data import clean_test_database, mock_users, start_test_database


class DatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        start_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clean_test_database()

    def test_get_user(self) -> None:
        user = get_user(id=1)
        self.assertEqual(mock_users[0], user)

        user = get_user(id=1)
        self.assertEqual(mock_users[0], user)

        user = get_user(id=1)
        self.assertEqual(mock_users[0], user)

        user = get_user(id=2)
        self.assertEqual(mock_users[1], user)

        user = get_user(id=2)
        self.assertEqual(mock_users[1], user)

        user = get_user(username=mock_users[1].username)
        self.assertEqual(mock_users[1], user)
        self.assertNotEqual(mock_users[2], user)
        self.assertNotEqual(mock_users[0], user)

        user = get_user(username=mock_users[2].username)
        self.assertEqual(mock_users[2], user)
        self.assertNotEqual(mock_users[3], user)
        self.assertNotEqual(mock_users[0], user)

        user = get_user(username=mock_users[2].username)
        self.assertEqual(mock_users[2], user)
        self.assertNotEqual(mock_users[3], user)
        self.assertNotEqual(mock_users[0], user)

    def test_update_user(self) -> None:
        user = get_user(username=mock_users[2].username)
        self.assertEqual(mock_users[2], user)

        update_user_info(
            id=3,
            username="testupdate",
            first_name="testfirstname",
            last_name="testlastname",
        )
        user = get_user(id=3)
        self.assertNotEqual(mock_users[2], user)
        self.assertEqual(user.username, "testupdate")
        self.assertEqual(user.first_name, "testfirstname")
        self.assertEqual(user.last_name, "testlastname")

    def test_update_user_dates(self) -> None:
        user = get_user(1)
        previous_buy_post = user.last_buy_post
        previous_sell_post = user.last_sell_post
        update_user_post_dates(user.id)
        user = get_user(1)
        self.assertEqual(user.last_buy_post, previous_buy_post)
        self.assertEqual(user.last_sell_post, previous_sell_post)

        update_user_post_dates(
            1,
            datetime(year=2022, month=11, day=11),
            datetime(year=2017, month=6, day=19),
        )
        user = get_user(1)
        self.assertEqual(user.last_buy_post, datetime(year=2022, month=11, day=11))
        self.assertEqual(user.last_sell_post, datetime(year=2017, month=6, day=19))

        reset_user_buy_post(1)
        user = get_user(1)
        self.assertEqual(user.last_buy_post, get_default_post_datetime())
        self.assertEqual(user.last_sell_post, datetime(year=2017, month=6, day=19))

        reset_user_sell_post(1)
        user = get_user(1)
        self.assertEqual(user.last_buy_post, get_default_post_datetime())
        self.assertEqual(user.last_sell_post, get_default_post_datetime())

    def test_roles(self) -> None:
        add_role_to_user(1, "seller")
        self.assertEqual(has_role(1, "seller"), True)
        self.assertEqual(has_role(1, "seller"), True)
        self.assertEqual(has_role(1, "judge"), False)

        add_role_to_user(2, "admin")
        self.assertEqual(has_role(2, "seller"), False)
        self.assertEqual(has_role(2, "judge"), False)
        self.assertEqual(has_role(2, "admin"), True)

        remove_role_from_user(2, "admin")
        self.assertEqual(has_role(2, "admin"), False)

        add_role_to_user(1, "judge")
        self.assertEqual(has_role(1, "seller"), True)
        self.assertEqual(has_role(1, "judge"), True)
        self.assertEqual(has_role(1, "admin"), False)

        remove_role_from_user(1, "judge")
        self.assertEqual(has_role(1, "seller"), True)
        self.assertEqual(has_role(1, "judge"), False)
        self.assertEqual(has_role(1, "admin"), False)
