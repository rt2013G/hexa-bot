import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from typing import Literal

# trunk-ignore(mypy/import-untyped)
# trunk-ignore(mypy/note)
import requests
from PIL import Image, UnidentifiedImageError
from telegram.ext import ContextTypes

from app.config import get_max_data_cache_size


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
    cached_searched_terms: dict[str, CardNameEntry]
    cached_card_data: dict[str, CardDataEntry]


type CropLevel = Literal[0, 1, 2, 3, 4]

CARD_DATA_CACHE: CardDataCache = CardDataCache(
    cached_searched_terms={}, cached_card_data={}
)


def get_cropped_image(image: Image, crop_level: CropLevel) -> Image:
    if crop_level == 0:
        return image

    width, height = image.size
    crop_level = 2 * crop_level
    random_pos = random.randint(0, int(max(
        (height * (crop_level - 1) / crop_level),
        (width * (crop_level - 1) / crop_level)
    )))
    crop_area = (random_pos, random_pos, random_pos + height / crop_level, random_pos + width / crop_level)
    cropped_image: Image = image.crop(crop_area)

    return cropped_image


def get_bytes_from_image(image: Image) -> bytes:
    byte_array = BytesIO()
    image.save(byte_array, format='BMP')
    return byte_array.getvalue()


def get_card_data(search_term: str) -> CardDataEntry | None:
    card_name: str | None = search_term
    if search_term in CARD_DATA_CACHE.cached_searched_terms.keys():
        card_name = CARD_DATA_CACHE.cached_searched_terms[search_term].card_name
        if card_name is None:
            return None
        if card_name in CARD_DATA_CACHE.cached_card_data.keys():
            return CARD_DATA_CACHE.cached_card_data[card_name]

    ENDPOINT_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    full_url = ENDPOINT_URL + "?fname=" + search_term
    response = requests.get(full_url, timeout=10)
    response_json = dict(json.loads(response.content))

    err: str | None = response_json.get("error")
    if err is not None:
        CARD_DATA_CACHE.cached_searched_terms[search_term] = CardNameEntry(
            card_name=None, time=datetime.now()
        )
        return None

    data = response_json["data"][0]
    card_name = data["name"]
    if card_name is None:
        return None
    image_url = data["card_images"][0]["image_url_cropped"]

    try:
        image = Image.open(requests.get(image_url, stream=True, timeout=10).raw)
    except UnidentifiedImageError:
        return None
    except Exception as err:
        logging.log(logging.ERROR, err)
        return None

    card_data = CardDataEntry(
        desc=data["desc"],
        image=image,
        time=datetime.now(),
    )
    CARD_DATA_CACHE.cached_card_data[card_name] = card_data
    CARD_DATA_CACHE.cached_searched_terms[search_term] = CardNameEntry(
        card_name=card_name, time=datetime.now()
    )

    cache_size = len(CARD_DATA_CACHE.cached_card_data)
    if cache_size > get_max_data_cache_size():
        halve_cache()

    return card_data


def get_cached_card_name(searched_term: str) -> str | None:
    cached_name = CARD_DATA_CACHE.cached_searched_terms.get(searched_term)
    if cached_name is not None:
        return cached_name.card_name
    return None


def halve_cache():
    to_delete = True
    for key in list(CARD_DATA_CACHE.cached_card_data.keys()):
        if to_delete:
            del CARD_DATA_CACHE.cached_card_data[key]

        to_delete = not to_delete

async def clean_card_data_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for key in list(CARD_DATA_CACHE.cached_card_data.keys()):
        if CARD_DATA_CACHE.cached_card_data[key].time < datetime.now() - timedelta(
            days=1
        ):
            del CARD_DATA_CACHE.cached_card_data[key]

    for key in list(CARD_DATA_CACHE.cached_searched_terms.keys()):
        if CARD_DATA_CACHE.cached_searched_terms[key].time < datetime.now() - timedelta(
            days=2
        ):
            del CARD_DATA_CACHE.cached_searched_terms[key]

    logging.log(logging.INFO, "Card data cache cleaned")