import unittest

from src.database.model import User
from src.utils.utils import clean_command_text, get_user_from_message_command
from tests.test_data import clean_test_database, mock_data, start_test_database


class UtilsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        start_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clean_test_database()

    def test_clean_command_text(self) -> None:
        commands = [
            "/command hello",
            "/search test",
            "/testtest",
            "/testcommand hello world  ",
        ]
        results = [
            clean_command_text(text=commands[0], command="/command"),
            clean_command_text(text=commands[1], command="/search"),
            clean_command_text(text=commands[2], command="/testtest"),
            clean_command_text(text=commands[3], command="/testcommand"),
        ]
        self.assertEqual(results[0], "hello")
        self.assertEqual(results[1], "test")
        self.assertEqual(results[2], "")
        self.assertEqual(results[3], "hello world  ")

    def test_get_user_from_command_arg(self) -> None:
        messages = [
            (f"/makeseller @{mock_data[2].username}", "/makeseller"),
            (f"/makeseller @{mock_data[0].id}", "/makeseller"),
            (f"/removeseller {mock_data[0].id}", "/removeseller"),
            (
                "/makeadmin bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "/makeadmin",
            ),
            (
                "/makescammer @bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "/makescammer",
            ),
            ("/resetdate @notlongbutdoesntexist", "/resetdate"),
            (f"/checkseller {mock_data[2].username}", "/checkseller"),
            ("/checkseller 15", "/checkseller"),
        ]
        users: list[User] = []
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
        self.assertEqual(users[7], None)
