import unittest

from app.message_helpers import get_user_from_command_arg, get_user_from_text
from tests.data import clear_test_database, create_test_database, mock_users


class UtilsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_test_database()

    def test_get_user_from_command_arg(self) -> None:
        self.assertEqual(get_user_from_command_arg("@fwfwwf"), None)
        self.assertEqual(
            get_user_from_command_arg(f"{mock_users[1].id}"), mock_users[1]
        )
        self.assertEqual(
            get_user_from_command_arg(f"{mock_users[1].username}"), mock_users[1]
        )
        self.assertEqual(
            get_user_from_command_arg("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"), None
        )

    def test_get_user_from_text(self) -> None:
        test_cases = [
            (
                f"#Feedback positivo per @{mock_users[1].username}, arrivato tutto perfettamente",
                mock_users[1].username,
            ),
            (
                f"#feedback positivo per @{mock_users[2].username}, tutto perfetto e pacco super professionale, consigliato 👌🏼",
                mock_users[2].username,
            ),
            (
                f"#feedback positivo per @{mock_users[1].username}: disponibile, spedizione rapida e carte arrivate come da richiesta. Consigliato.",
                mock_users[1].username,
            ),
        ]
        for test_case in test_cases:
            self.assertEqual(get_user_from_text(test_case[0]).username, test_case[1])
