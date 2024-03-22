import unittest
from datetime import datetime

from app.constants import Dates
from app.database import (MarketPlusPost, get_posts_to_delete,
                          get_posts_to_send, insert_market_plus_post,
                          update_delete_market_plus_post, update_posted_date)
from tests.data import (clear_test_database, create_test_database,
                        get_connection)


class MarketPlusPostTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_test_database()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM market_plus_post WHERE message_id=1;")
                cur.execute("DELETE FROM market_plus_post WHERE message_id=2;")
                cur.execute("DELETE FROM market_plus_post WHERE message_id=3;")

    def test_market_plus(self) -> None:
        insert_market_plus_post(1, end_date=datetime(year=2025, month=10, day=10))
        insert_market_plus_post(2, end_date=datetime(year=2005, month=10, day=10))
        insert_market_plus_post(3, end_date=datetime(year=2012, month=10, day=10))
        posts: list[MarketPlusPost] = get_posts_to_send()
        self.assertEqual(len(posts), 1)
        post: MarketPlusPost = posts[0]
        self.assertEqual(post.message_id, 1)
        self.assertEqual(post.end_date, datetime(year=2025, month=10, day=10))
        self.assertEqual(post.last_posted_date, Dates.MARKET_EPOCH)

        update_posted_date(1, 1, datetime.now())
        posts: MarketPlusPost = get_posts_to_send()
        self.assertEqual(len(posts), 0)

        posts_to_delete = get_posts_to_delete()
        self.assertEqual(len(posts_to_delete), 2)
        ids = [post.message_id for post in posts_to_delete]
        self.assertEqual(1 in ids, False)
        self.assertEqual(2 in ids, True)
        self.assertEqual(3 in ids, True)

        update_delete_market_plus_post(2)
        self.assertEqual(len(get_posts_to_delete()), 1)

        update_delete_market_plus_post(3)
        self.assertEqual(len(get_posts_to_delete()), 0)
