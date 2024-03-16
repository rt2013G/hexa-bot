import unittest
from datetime import datetime

from app.config import get_default_post_datetime
from app.database.models.market_plus_post import (
    MarketPlusPost,
    get_active_market_plus_posts,
    insert_market_plus_post,
    update_market_plus_posted_date,
)
from tests.test_data import clean_test_database, get_connection, start_test_database


class MarketPlusPostTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        start_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clean_test_database()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM market_plus_post WHERE message_id=1;")
                cur.execute("DELETE FROM market_plus_post WHERE message_id=2;")
                cur.execute("DELETE FROM market_plus_post WHERE message_id=3;")

    def test_market_plus(self) -> None:
        insert_market_plus_post(1, end_date=datetime(year=2025, month=10, day=10))
        insert_market_plus_post(2, end_date=datetime(year=2005, month=10, day=10))
        insert_market_plus_post(3, end_date=datetime(year=2012, month=10, day=10))
        posts: list[MarketPlusPost] = get_active_market_plus_posts()
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post.message_id, 1)
        self.assertEqual(post.end_date, datetime(year=2025, month=10, day=10))
        self.assertEqual(post.last_posted_date, get_default_post_datetime())

        update_market_plus_posted_date(1, datetime(year=2020, month=5, day=2))
        post: MarketPlusPost = get_active_market_plus_posts()[0]
        self.assertEqual(post.last_posted_date, datetime(year=2020, month=5, day=2))
