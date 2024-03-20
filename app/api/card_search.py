import asyncio
import json
import logging
import random
from dataclasses import dataclass
from io import BytesIO
from typing import Literal

import requests
from PIL import Image, UnidentifiedImageError

type CropLevel = Literal[0, 1, 2, 3, 4]

@dataclass
class CardData:
    name: str
    desc: str
    image: Image


async def fetch_card_data(search_word: str) -> CardData | None:
    ENDPOINT_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    full_url = ENDPOINT_URL + "?fname=" + search_word
    result = await asyncio.to_thread(requests.get, url=full_url, timeout=10)
    if result is None or result.content is None:
        return None
    
    response = dict(json.loads(result.content))
    if response.get("error"):
        return None
    
    data: list = response.get("data")
    # Removes ambiguity by returning None if two or more cards were found
    if data is None or len(data) == 0 or len(data) >= 2:
        return None
    data: dict = data[0]

    card_name = data.get("name")
    card_description = data.get("desc")
    if card_name is None or card_description is None:
        return None
    
    card_image_urls = data.get("card_images")
    if card_image_urls is None or len(card_image_urls) == 0:
        return None
    
    card_image_urls: dict = card_image_urls[0]
    cropped_image_url = card_image_urls.get("image_url_cropped")
    if cropped_image_url is None:
        return None
    
    image_result = await asyncio.to_thread(requests.get, url=cropped_image_url, stream=True, timeout=10)
    if image_result is None:
        return None
    
    try:
        image = Image.open(image_result.raw)
    except UnidentifiedImageError:
        return None
    except Exception as err:
        logging.log(logging.ERROR, err)
        return None
    
    return CardData(name=card_name, desc=card_description, image=image)


def get_cropped_image_bytes(image: Image, crop_level: CropLevel) -> bytes:
    byte_array = BytesIO()

    if crop_level == 0:
        image.save(byte_array, format='BMP')
        return byte_array.getvalue()

    width, height = image.size
    crop_level = 2 * crop_level
    random_pos = random.randint(0, int(max(
        (height * (crop_level - 1) / crop_level),
        (width * (crop_level - 1) / crop_level)
    )))
    crop_area = (random_pos, random_pos, random_pos + height / crop_level, random_pos + width / crop_level)
    cropped_image: Image = image.crop(crop_area)

    cropped_image.save(byte_array, format='BMP')
    return byte_array.getvalue()