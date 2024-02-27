import unittest
from datetime import datetime
from dotenv import load_dotenv
from src import config
from src.utils.utils import is_role
from src.database.dbms import (
    get_connection, init_db, 
    insert_user, get_user_from_id, make_role, remove_role, get_role_list, 
    update_user_dates, update_user_info
    )
from dataclasses import dataclass

@dataclass
class MockUser:
    id: int
    username: str | None
    first_name: str | None
    last_name: str | None

mock_data = [
    MockUser(1, None, None, "test11"),
    MockUser(2, "test2", None, None),
    MockUser(3, "username", "test333", None),
    MockUser(4, None, "test4", "test44"),
]

class DatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
        config.GLOBAL_CONFIGS = config.load_configs()
        init_db()
        for mock_user in mock_data:
            insert_user(mock_user.id, mock_user.username, mock_user.first_name, mock_user.last_name)


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

    def reset_users(self) -> None:
        for mock_user in mock_data:
            update_user_info(mock_user.id, mock_user.username, mock_user.first_name, mock_user.last_name)

    def test_get_user_function(self):
        user = get_user_from_id(10)
        self.assertEqual(user, None)


    def test_user_class(self):
        user = get_user_from_id(1)
        self.assertEqual(user.username, mock_data[0].username)
        self.assertEqual(user.first_name, mock_data[0].first_name)
        self.assertEqual(user.last_name, mock_data[0].last_name)
        self.assertEqual(user.last_buy_post.year, 2015)
        self.assertEqual(user.last_buy_post.month, 1)
        self.assertEqual(user.last_buy_post.day, 15)
        self.assertEqual(user.last_sell_post.year, 2015)
        self.assertEqual(user.last_sell_post.month, 1)
        self.assertEqual(user.last_sell_post.day, 15)

        user = get_user_from_id(2)
        self.assertEqual(user.username, mock_data[1].username)
        self.assertEqual(user.first_name, mock_data[1].first_name)
        self.assertEqual(user.last_name, mock_data[1].last_name)
        self.assertEqual(user.last_buy_post.year, 2015)
        self.assertEqual(user.last_buy_post.month, 1)
        self.assertEqual(user.last_buy_post.day, 15)
        self.assertEqual(user.last_sell_post.year, 2015)
        self.assertEqual(user.last_sell_post.month, 1)
        self.assertEqual(user.last_sell_post.day, 15)


    def test_seller_role(self):
        self.assertEqual(len(get_role_list("seller")), 0)
        make_role(1, "seller")
        self.assertEqual(len(get_role_list("seller")), 1)
        make_role(3, "seller")
        self.assertEqual(len(get_role_list("seller")), 2)

        seller_list = get_role_list("seller")

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
        update_user_dates(1, datetime(year=2022, month=6, day=2), datetime(year=2021, month=1, day=12))
        user = get_user_from_id(1)
        self.assertEqual(user.last_buy_post, datetime(year=2022, month=6, day=2))
        self.assertEqual(user.last_sell_post, datetime(year=2021, month=1, day=12))

        update_user_dates(1)
        user = get_user_from_id(1)
        self.assertEqual(user.last_buy_post, datetime(year=2015, month=1, day=15))
        self.assertEqual(user.last_sell_post, datetime(year=2015, month=1, day=15))

    def test_update_user(self):
        update_user_info(1, username="newusername", first_name=mock_data[0].first_name, last_name=mock_data[0].last_name)
        user = get_user_from_id(1)
        self.assertEqual(user.username, "newusername")
        self.assertEqual(user.first_name, mock_data[0].first_name)
        self.assertEqual(user.last_name, mock_data[0].last_name)
        self.reset_users()
        
        update_user_info(2, username=mock_data[1].username ,first_name="update", last_name="updatelastname")
        user = get_user_from_id(2)
        self.assertEqual(user.username, mock_data[1].username)
        self.assertEqual(user.first_name, "update")
        self.assertEqual(user.last_name, "updatelastname") 
        self.reset_users()

    def test_remove_role(self):
        make_role(2, "seller")
        make_role(2, "admin")
        self.assertEqual(is_role(2, "admin"), True)
        remove_role(2, "admin")
        self.assertEqual(is_role(2, "admin"), False)
        self.assertEqual(is_role(2, "seller"), True)
        remove_role(2, "seller")
        self.assertEqual(is_role(2, "seller"), False)
        