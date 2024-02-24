import unittest
from datetime import datetime
from dotenv import load_dotenv
from src.database.dbms import get_connection, init_db, insert_user, get_user_from_id

class DatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
        init_db()
        insert_user("1", "test1", "test11", None)
        insert_user("2", "test2", "test22", "test222", datetime.now())

    @classmethod
    def tearDownClass(cls) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id=1;")
                cur.execute("DELETE FROM users WHERE id=2;")  

    def test_user_class(self):
        user = get_user_from_id(1)
        self.assertEqual(user.username, None)
        self.assertEqual(user.first_name, "test1")
        self.assertEqual(user.last_name, "test11")
        self.assertEqual(user.last_buy_post.year, 2015)
        self.assertEqual(user.last_buy_post.month, 1)
        self.assertEqual(user.last_buy_post.day, 15)
        self.assertEqual(user.last_sell_post.year, 2015)
        self.assertEqual(user.last_sell_post.month, 1)
        self.assertEqual(user.last_sell_post.day, 15)

    def test_user_class_2(self):
        user = get_user_from_id(2)
        self.assertFalse(user.username is None)
        self.assertEqual(type(user.last_buy_post), datetime)
        