import unittest

from src.database.models.role import (
    get_role_list,
    get_roles_for_user,
    make_role,
    remove_role,
)
from tests.test_data import clean_test_database, start_test_database


class RoleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        start_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clean_test_database()

    def test_make_and_remove_role(self):
        self.assertEqual(len(get_role_list("seller")), 0)
        make_role(1, "seller")
        self.assertEqual(len(get_role_list("seller")), 1)
        make_role(3, "seller")
        self.assertEqual(len(get_role_list("seller")), 2)

        self.assertEqual(len(get_role_list("judge")), 0)
        make_role(2, "judge")
        self.assertEqual(len(get_role_list("judge")), 1)
        make_role(3, "judge")
        self.assertEqual(len(get_role_list("judge")), 2)

        remove_role(4, "judge")
        self.assertEqual(len(get_role_list("judge")), 2)

        remove_role(3, "judge")
        self.assertEqual(len(get_role_list("judge")), 1)
        remove_role(2, "judge")
        self.assertEqual(len(get_role_list("judge")), 0)
        remove_role(1, "seller")
        self.assertEqual(len(get_role_list("seller")), 1)
        remove_role(3, "seller")
        self.assertEqual(len(get_role_list("seller")), 0)

    def test_get_roles_for_user(self):
        make_role(2, "judge")
        roles = get_roles_for_user(2)
        self.assertEqual(len(roles), 1)

        make_role(2, "admin")
        make_role(2, "seller")
        make_role(2, "scammer")
        roles = get_roles_for_user(2)
        self.assertEqual(len(roles), 4)

        remove_role(2, "judge")
        remove_role(2, "admin")
        remove_role(2, "seller")
        remove_role(2, "scammer")
        roles = get_roles_for_user(2)
        self.assertEqual(len(roles), 0)

        make_role(1, "admin")
        make_role(1, "seller")
        roles = get_roles_for_user(1)
        self.assertEqual("admin" in roles, True)
        self.assertEqual("seller" in roles, True)
        self.assertEqual("judge" in roles, False)
        self.assertEqual("scammer" in roles, False)

        remove_role(1, "admin")
        remove_role(1, "seller")
        roles = get_roles_for_user(1)
        self.assertEqual(len(roles), 0)
