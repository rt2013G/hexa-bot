import unittest
from datetime import datetime, timedelta

from app.database import get_guess_game_rankings, insert_game, insert_user_score
from tests.data import clear_test_database, create_test_database


class GuessGameTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clear_test_database()

    def test_get_guess_game_scores(self) -> None:
        date = datetime.now()
        date2 = date + timedelta(days=1)
        date3 = date + timedelta(days=2)
        insert_game(date=date)
        insert_game(date=date2)
        insert_game(date=date3)
        insert_user_score(user_id=1, score=10, game_date=date)
        insert_user_score(user_id=1, score=254, game_date=date2)
        insert_user_score(user_id=1, score=82, game_date=date3)

        insert_user_score(user_id=2, score=50, game_date=date)
        insert_user_score(user_id=2, score=20, game_date=date2)

        insert_user_score(user_id=3, score=20, game_date=date2)
        insert_user_score(user_id=3, score=77, game_date=date3)

        insert_user_score(user_id=4, score=2, game_date=date)
        insert_user_score(user_id=4, score=1, game_date=date3)

        rankings = get_guess_game_rankings(2)
        self.assertEqual(len(rankings), 2)
        self.assertEqual(rankings[1], 346)
        self.assertEqual(rankings[3], 97)

        rankings = get_guess_game_rankings(10)
        self.assertEqual(len(rankings), 4)
        self.assertEqual(rankings[1], 346)
        self.assertEqual(rankings[3], 97)
        self.assertEqual(rankings[2], 70)
        self.assertEqual(rankings[4], 3)
