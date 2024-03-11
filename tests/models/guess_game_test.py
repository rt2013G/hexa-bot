import unittest
from datetime import datetime, timedelta

from app.database.models.guess_game import (
    get_guess_game_rankings,
    get_total_score_for_user,
    insert_game,
    insert_user_score_into_game,
)
from tests.test_data import clean_test_database, start_test_database


class GuessGameTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        start_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        clean_test_database()

    def test_get_guess_game_scores(self) -> None:
        date = datetime.now()
        date2 = date + timedelta(days=1)
        date3 = date + timedelta(days=2)
        insert_game(date=date)
        insert_game(date=date2)
        insert_game(date=date3)
        insert_user_score_into_game(user_id=1, score=10, game_date=date)
        insert_user_score_into_game(user_id=1, score=254, game_date=date2)
        insert_user_score_into_game(user_id=1, score=82, game_date=date3)

        insert_user_score_into_game(user_id=2, score=50, game_date=date)
        insert_user_score_into_game(user_id=2, score=20, game_date=date2)

        insert_user_score_into_game(user_id=3, score=20, game_date=date2)
        insert_user_score_into_game(user_id=3, score=77, game_date=date3)

        insert_user_score_into_game(user_id=4, score=2, game_date=date)
        insert_user_score_into_game(user_id=4, score=1, game_date=date3)

        self.assertEqual(get_total_score_for_user(user_id=1), 346)
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
