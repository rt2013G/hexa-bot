import unittest
from datetime import datetime

from app.cache import get_user, update_user_date, update_user_info
from app.constants import Dates
from tests.data import clear_test_database, create_test_database, mock_users


class UsersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_test_database()

    def test_get_user(self) -> None:
        user = mock_users[0]
        test_user = get_user(id=mock_users[0].id)
        self.assertEqual(test_user.id, user.id)
        self.assertEqual(test_user.username, user.username)
        self.assertEqual(test_user.first_name, user.first_name)
        self.assertEqual(test_user.last_name, user.last_name)
        self.assertEqual(test_user.last_buy_post, Dates.MARKET_EPOCH)
        self.assertEqual(test_user.last_sell_post, Dates.MARKET_EPOCH)

        user = get_user(id=10)
        self.assertEqual(user, None)

        user = get_user(username="thisusernamedoesntexist")
        self.assertEqual(user, None)

        user = get_user(username=mock_users[1].username)
        self.assertEqual(user, mock_users[1])

    def test_update_info(self) -> None:
        user = get_user(id=mock_users[0].id)
        self.assertEqual(user, mock_users[0])

        update_user_info(
            id=user.id,
            username="newusername",
            first_name=user.first_name,
            last_name=user.last_name,
        )

        test_user = get_user(id=user.id)
        self.assertEqual(test_user.username, "newusername")
        self.assertEqual(test_user.first_name, user.first_name)
        self.assertEqual(test_user.last_name, user.last_name)

    def test_update_date(self) -> None:
        user = get_user(id=mock_users[0].id)
        update_user_date(
            id=user.id,
            last_buy_post=datetime(year=2016, month=4, day=1),
            last_sell_post=datetime(year=2016, month=1, day=3),
        )

        user = get_user(id=mock_users[0].id)
        self.assertEqual(user.last_buy_post, datetime(year=2016, month=4, day=1))
        self.assertEqual(user.last_sell_post, datetime(year=2016, month=1, day=3))
