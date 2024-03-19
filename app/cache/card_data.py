from dataclasses import dataclass
from datetime import datetime

from PIL import Image


@dataclass
class CardDataEntry:
    desc: str
    image: Image
    time: datetime


@dataclass
class CardNameEntry:
    card_name: str | None
    time: datetime


@dataclass
class CardDataCache:
    card_data: dict[str, CardDataEntry]
    search_words: dict[str, CardNameEntry]


card_data_cache = CardDataCache(card_data={}, search_words={})


def insert_card_data(card_name: str, desc: str, image: Image) -> None:
    pass


def get_card_desc(card_name: str) -> str:
    pass


def get_card_image(card_name: str) -> Image:
    pass


def insert_card_name(search_word: str, card_name: str | None) -> None:
    pass
