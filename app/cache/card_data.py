from dataclasses import dataclass
from datetime import datetime

from app.api import CardData, fetch_card_data


@dataclass
class CardDataEntry:
    card_data: CardData | None
    time: datetime


@dataclass
class CardNameEntry:
    card_name: str | None
    time: datetime


@dataclass
class CardDataCache:
    cards: dict[str, CardDataEntry]
    words: dict[str, CardNameEntry]


search_cache = CardDataCache(cards={}, words={})


async def get_card_data(search_word: str) -> CardData | None:
    if card_name_entry := search_cache.words.get(search_word):
        if card_name_entry.card_name is None:
            return None
        if card_data_entry := search_cache.cards.get(card_name_entry.card_name):
            return card_data_entry.card_data

    card_data = await fetch_card_data(search_word=search_word)

    if card_data is None:
        search_cache.words[search_word] = CardNameEntry(
            card_name=None, time=datetime.now()
        )
    else:
        search_cache.words[search_word] = CardNameEntry(
            card_name=card_data.name, time=datetime.now()
        )
        search_cache.cards[card_data.name] = CardDataEntry(
            card_data=card_data, time=datetime.now()
        )

    return card_data
