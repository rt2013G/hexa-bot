import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

# trunk-ignore(mypy/import-untyped)
# trunk-ignore(mypy/note)
import requests
from telegram.ext import ContextTypes


@dataclass
class CardData:
    name: str
    desc: str
    time: datetime


ENDPOINT_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
CARD_DATA_CACHE: dict[str, CardData] = {}


def get_card_data(card_name: str) -> CardData | None:
    if card_name in CARD_DATA_CACHE.keys():
        return CARD_DATA_CACHE[card_name]

    full_url = ENDPOINT_URL + "?fname=" + card_name
    response = requests.get(full_url, timeout=10)
    response_json = dict(json.loads(response.content))

    err: str | None = response_json.get("error")
    if err is not None:
        return None

    data = response_json["data"][0]
    card_data = CardData(name=data["name"], desc=data["desc"], time=datetime.now())
    CARD_DATA_CACHE[card_name] = card_data
    return card_data


async def clean_card_data_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for key in list(CARD_DATA_CACHE):
        if CARD_DATA_CACHE[key].time < datetime.now() - timedelta(days=1):
            del CARD_DATA_CACHE[key]
    logging.log(logging.INFO, "Card data cache cleaned")
