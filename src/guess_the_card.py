import random
from io import BytesIO
from typing import Literal

from PIL import Image

type CropLevel = Literal[0, 1, 2, 3, 4]

def get_random_card_name() -> str:
    pass


def get_cropped_image(image: Image, crop_level: CropLevel) -> Image:
    if crop_level == 0:
        return image
    
    width, height = image.size
    crop_level = 2 * crop_level
    random_top_left_corner = random.randint(0, int(max(
        (height * (crop_level - 1) / crop_level),
        (width * (crop_level - 1) / crop_level)
    )))
    crop_area = (random_top_left_corner, random_top_left_corner, height / crop_level, width / crop_level)
    cropped_image: Image = image.crop(crop_area)

    return cropped_image

def get_bytes_from_image(image: Image) -> bytes:
    byte_array = BytesIO()
    image.save(byte_array, format='BMP')
    return byte_array.getvalue()