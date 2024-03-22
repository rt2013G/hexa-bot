import unittest
from datetime import datetime

from app.database import (
    get_user_from_id,
    get_user_from_username,
    update_user_info,
    update_user_last_buy_post,
    update_user_last_sell_post,
)
from tests.data import clear_test_database, create_test_database, mock_users


class UserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_test_database()

    def test_get_user_from_id(self) -> None:
        user = get_user_from_id(id=mock_users[0].id)
        self.assertEqual(mock_users[0], user)

        user = get_user_from_id(id=mock_users[0].id)
        self.assertEqual(mock_users[0], user)

        user = get_user_from_id(id=mock_users[0].id)
        self.assertEqual(mock_users[0], user)

        user = get_user_from_id(id=mock_users[1].id)
        self.assertEqual(mock_users[1], user)

        user = get_user_from_id(id=mock_users[1].id)
        self.assertEqual(mock_users[1], user)

    def test_get_user_from_username(self) -> None:
        user = get_user_from_username(username=mock_users[1].username)
        self.assertEqual(mock_users[1], user)
        self.assertNotEqual(mock_users[2], user)
        self.assertNotEqual(mock_users[0], user)

        user = get_user_from_username(username=mock_users[2].username)
        self.assertEqual(mock_users[2], user)
        self.assertNotEqual(mock_users[3], user)
        self.assertNotEqual(mock_users[0], user)

    def test_update_user(self) -> None:
        user = get_user_from_username(username=mock_users[2].username)
        self.assertEqual(mock_users[2], user)

        update_user_info(
            id=mock_users[2].id,
            username="testupdate",
            first_name="testfirstname",
            last_name="testlastname",
        )
        user = get_user_from_id(id=mock_users[2].id)
        self.assertEqual(user.username, "testupdate")
        self.assertEqual(user.first_name, "testfirstname")
        self.assertEqual(user.last_name, "testlastname")

    def test_update_user_dates(self) -> None:
        user = get_user_from_id(mock_users[0].id)
        previous_buy_post = user.last_buy_post
        previous_sell_post = user.last_sell_post

        update_user_last_buy_post(
            id=mock_users[0].id, last_buy_post=datetime(year=2022, month=11, day=11)
        )
        update_user_last_sell_post(
            id=mock_users[0].id, last_sell_post=datetime(year=2017, month=6, day=19)
        )

        user = get_user_from_id(mock_users[0].id)
        self.assertNotEqual(user.last_buy_post, previous_buy_post)
        self.assertNotEqual(user.last_sell_post, previous_sell_post)
        self.assertEqual(user.last_buy_post, datetime(year=2022, month=11, day=11))
        self.assertEqual(user.last_sell_post, datetime(year=2017, month=6, day=19))
