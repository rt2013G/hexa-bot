import unittest

from app.card_search import get_card_data


class CardSearchTest(unittest.TestCase):
    def test_search_card_data(self) -> None:
        card_data = get_card_data("thisisnotarealcard")
        self.assertEqual(card_data, None)

        card_data = get_card_data("candina")
        self.assertEqual(
            card_data.desc,
            'When this card is Normal Summoned: You can add 1 "Trickstar" card from your Deck to your hand. Each time your opponent activates a Spell/Trap Card, inflict 200 damage to them immediately after it resolves.',
        )
