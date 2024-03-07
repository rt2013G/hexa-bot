import unittest
from datetime import datetime, timedelta

from src.database import User, update_user_post_dates
from src.utils import (
    clean_command_text,
    get_user_from_message_command,
    has_sent_buy_post_today,
    has_sent_sell_post_today,
)
from tests.test_data import clean_test_database, mock_users, start_test_database


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
            (f"/makeseller @{mock_users[2].username}", "/makeseller"),
            (f"/makeseller @{mock_users[0].id}", "/makeseller"),
            (f"/removeseller {mock_users[0].id}", "/removeseller"),
            (
                "/makeadmin bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "/makeadmin",
            ),
            (
                "/makescammer @bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "/makescammer",
            ),
            ("/resetdate @notlongbutdoesntexist", "/resetdate"),
            (f"/checkseller {mock_users[2].username}", "/checkseller"),
            ("/checkseller 15", "/checkseller"),
            ("/reject @username", "/reject"),
        ]
        users: list[User] = []
        for message in messages:
            users.append(get_user_from_message_command(message[0], message[1]))

        self.assertEqual(users[0], mock_users[2])
        self.assertEqual(users[1], None)
        self.assertEqual(users[2], mock_users[0])
        self.assertEqual(users[3], None)
        self.assertEqual(users[4], None)
        self.assertEqual(users[5], None)
        self.assertEqual(users[6], None)
        self.assertEqual(users[7], None)
        self.assertEqual(users[8], mock_users[2])

    def test_has_sent_posts_today(self) -> None:
        update_user_post_dates(1, datetime.now(), datetime.now() - timedelta(days=5))
        update_user_post_dates(2, datetime.now(), datetime.now())
        update_user_post_dates(3, datetime.now() - timedelta(days=10), datetime.now())
        update_user_post_dates(
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
