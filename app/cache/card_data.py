from dataclasses import dataclass
from datetime import datetime

from app.api import CardData, fetch_card_data


@dataclass
class CardDataEntry:
    card_data: CardData | None
    time: datetime


@dataclass
class CardDataCache:
    cards: dict[str, CardDataEntry]
    words: dict[str, str]


search_cache = CardDataCache(cards={}, words={})


async def get_card_data(search_word: str) -> CardData | None:
    if card_name := search_cache.words.get(search_word):
        if card_data_entry := search_cache.cards.get(card_name):
            return card_data_entry.card_data

    card_data = await fetch_card_data(search_word=search_word)
    search_cache.words[search_word] = card_data.name
    search_cache.cards[card_data.name] = CardDataEntry(
        card_data=card_data, time=datetime.now()
    )
    return card_data
