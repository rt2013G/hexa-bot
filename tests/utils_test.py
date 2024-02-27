import unittest
from dotenv import load_dotenv
from src import config
from src.utils.utils import get_user_from_message_command
from src.database.dbms import init_db, get_connection, insert_user
from tests.database_test import mock_data
from src.database.model import User

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
                cur.execute("DELETE FROM users WHERE id=1;")
                cur.execute("DELETE FROM users WHERE id=2;")  
                cur.execute("DELETE FROM users WHERE id=3;")
                cur.execute("DELETE FROM users WHERE id=4;")

    
    def test_get_user_from_command_arg(self):
        messages = [
            (f"/makeseller @{mock_data[2].username}", "/makeseller"),
            (f"/makeseller @{mock_data[0].id}", "/makeseller"),
            (f"/removeseller {mock_data[0].id}", "/removeseller"),
            ("/makeadmin bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "/makeadmin"),
            ("/makescammer @bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "/makescammer"),
            ("/resetdate @notlongbutdoesntexist", "/resetdate"),
            (f"/checkseller {mock_data[2].username}", "/checkseller")
        ]
        users : list[User] = []
        for message in messages:
            users.append(get_user_from_message_command(message[0], message[1]))

        self.assertEqual(users[0].id, mock_data[2].id)
        self.assertEqual(users[0].username, mock_data[2].username)
        self.assertEqual(users[0].first_name, mock_data[2].first_name)
        self.assertEqual(users[0].last_name, mock_data[2].last_name)
        self.assertEqual(users[1], None)
        self.assertEqual(users[2].id, mock_data[0].id)
        self.assertEqual(users[2].username, mock_data[0].username)
        self.assertEqual(users[2].first_name, mock_data[0].first_name)
        self.assertEqual(users[2].last_name, mock_data[0].last_name)
        self.assertEqual(users[3], None)
        self.assertEqual(users[4], None)
        self.assertEqual(users[5], None)
        self.assertEqual(users[6], None)
