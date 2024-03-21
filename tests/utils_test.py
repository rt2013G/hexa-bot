import unittest
from datetime import datetime, timedelta

from app.cache import update_user_date
from app.utils import has_sent_buy_post_today, has_sent_sell_post_today
from tests.data import clear_test_database, create_test_database


class UtilsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_test_database()

    def test_has_sent_posts_today(self) -> None:
        update_user_date(1, datetime.now(), datetime.now() - timedelta(days=5))
        update_user_date(2, datetime.now(), datetime.now())
        update_user_date(3, datetime.now() - timedelta(days=10), datetime.now())
        update_user_date(
            4, datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=1)
        )

        self.assertEqual(has_sent_buy_post_today(1), True)
        self.assertEqual(has_sent_sell_post_today(1), False)

        self.assertEqual(has_sent_buy_post_today(2), True)
        self.assertEqual(has_sent_sell_post_today(2), True)

        self.assertEqual(has_sent_buy_post_today(3), False)
        self.assertEqual(has_sent_sell_post_today(3), True)

        self.assertEqual(has_sent_buy_post_today(4), False)
        self.assertEqual(has_sent_sell_post_today(4), False)