import unittest
from datetime import datetime
from dotenv import load_dotenv
from src.utils import config
from src.database.dbms import get_connection, init_db, insert_user, get_user_from_id, make_role, get_role_list, set_dates_for_user

class DatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
        config.GLOBAL_CONFIGS = config.load_configs()
        init_db()
        insert_user(1, "test1", "test11", None)
        insert_user(2, "test2", "test22", "test222", datetime.now())
        insert_user(3, "test3", "test33", "test333", datetime.now(), datetime.now())
        insert_user(4, "test3", "test33", None)


    @classmethod
    def tearDownClass(cls) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users_role WHERE user_id=1;")
                cur.execute("DELETE FROM users_role WHERE user_id=2;")
                cur.execute("DELETE FROM users_role WHERE user_id=3;")
                cur.execute("DELETE FROM users WHERE id=1;")
                cur.execute("DELETE FROM users WHERE id=2;")  
                cur.execute("DELETE FROM users WHERE id=3;")
                cur.execute("DELETE FROM users WHERE id=4;")


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

        user = get_user_from_id(2)
        self.assertFalse(user.username is None)
        self.assertEqual(type(user.last_buy_post), datetime)  


    def test_seller_role(self):
        self.assertEqual(len(get_role_list("seller")), 0)
        make_role(1, "seller")
        self.assertEqual(len(get_role_list("seller")), 1)
        make_role(3, "seller")
        self.assertEqual(len(get_role_list("seller")), 2)

        seller_list = get_role_list("seller")
        for seller in seller_list:
            self.assertEqual(type(seller.id), int)
            self.assertEqual(type(seller.first_name), str)
            self.assertEqual(type(seller.last_name), str)
            self.assertEqual(type(seller.last_buy_post), datetime)
            self.assertEqual(type(seller.last_sell_post), datetime)

        id_list = []
        for seller in seller_list:
            id_list.append(seller.id)
        self.assertEqual(1 in id_list, True)
        self.assertEqual(2 in id_list, False)
        self.assertEqual(3 in id_list, True)
        self.assertEqual(4 in id_list, False)

    def test_judge_role(self):
        self.assertEqual(len(get_role_list("judge")), 0)
        make_role(2, "judge")
        self.assertEqual(len(get_role_list("judge")), 1)
        make_role(3, "judge")
        self.assertEqual(len(get_role_list("judge")), 2)

        judge_list = get_role_list("judge")
        id_list = []
        for seller in judge_list:
            id_list.append(seller.id)
        self.assertEqual(1 in id_list, False)
        self.assertEqual(2 in id_list, True)
        self.assertEqual(3 in id_list, True)
        self.assertEqual(4 in id_list, False)

    def test_set_date(self):
        set_dates_for_user(1, datetime(year=2022, month=6, day=2), datetime(year=2021, month=1, day=12))
        user = get_user_from_id(1)
        self.assertEqual(user.last_buy_post, datetime(year=2022, month=6, day=2))
        self.assertEqual(user.last_sell_post, datetime(year=2021, month=1, day=12))

        set_dates_for_user(1)
        user = get_user_from_id(1)
        self.assertEqual(user.last_buy_post, datetime(year=2015, month=1, day=15))
        self.assertEqual(user.last_sell_post, datetime(year=2015, month=1, day=15))
