import unittest

from app.constants import Roles
from app.database import get_roles, insert_role, remove_role
from tests.data import clear_test_database, create_test_database, mock_users


class RolesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_test_database()

    def test_roles(self) -> None:
        insert_role(mock_users[0].id, Roles.SELLER)
        roles = get_roles(mock_users[0].id)
        self.assertEqual(Roles.SELLER in roles, True)
        self.assertEqual(Roles.SCAMMER in roles, False)

        insert_role(mock_users[0].id, Roles.ADMIN)
        roles = get_roles(mock_users[0].id)
        self.assertEqual(Roles.SELLER in roles, True)
        self.assertEqual(Roles.ADMIN in roles, True)
        self.assertEqual(Roles.JUDGE in roles, False)

        remove_role(mock_users[0].id, Roles.ADMIN)
        roles = get_roles(mock_users[0].id)
        self.assertEqual(Roles.SELLER in roles, True)
        self.assertEqual(Roles.ADMIN in roles, False)

        remove_role(mock_users[0].id, Roles.SELLER)
        roles = get_roles(mock_users[0].id)
        self.assertEqual(Roles.SELLER in roles, False)
