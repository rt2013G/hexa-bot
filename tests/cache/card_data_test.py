import unittest
from datetime import datetime

from app.api import CardData
from app.cache import get_card_data


class CardDataTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_card_data(self) -> None:
        card_data = await get_card_data("thisisnotarealcard")
        self.assertEqual(card_data, None)

        card_data: CardData = await get_card_data("candina")
        self.assertEqual(
            card_data.desc,
            'When this card is Normal Summoned: You can add 1 "Trickstar" card from your Deck to your hand. Each time your opponent activates a Spell/Trap Card, inflict 200 damage to them immediately after it resolves.',
        )

        start_time = datetime.now()
        card_data: CardData = await get_card_data("candina")
        time_ms = (datetime.now() - start_time).microseconds / 1000
        self.assertEqual(time_ms < 10, True)
