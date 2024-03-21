import json
import logging
import os
import sys


def load_configs() -> dict:
    debug = True if len(sys.argv) >= 3 and sys.argv[2] == "debug" else False
    path = (
        "app/static/debug_config.json" if debug else "app/static/deployment_config.json"
    )
    if not os.path.exists(os.path.abspath(path)):
        logging.log(
            logging.ERROR, "Error. Configuration file not present in app/static."
        )
    with open(os.path.abspath(path), "r") as f:
        return dict(json.load(f))


GLOBAL_CONFIGS: dict = load_configs()


def get_main_id() -> int:
    return int(GLOBAL_CONFIGS["group_info"]["main_id"])


def get_market_id() -> int:
    return int(GLOBAL_CONFIGS["group_info"]["market_id"])


def get_approval_id() -> int:
    return int(GLOBAL_CONFIGS["group_info"]["approval_id"])


def get_feedback_channel_id() -> int:
    return int(GLOBAL_CONFIGS["channel_info"]["feedback_id"])


def get_logging_channel_id() -> int:
    return int(GLOBAL_CONFIGS["channel_info"]["logging_id"])


def get_photo_storage_id() -> int:
    return int(GLOBAL_CONFIGS["channel_info"]["photo_storage_id"])


def get_market_plus_id() -> int:
    return int(GLOBAL_CONFIGS["channel_info"]["market_plus_id"])


def get_debug_user_id() -> int:
    return int(GLOBAL_CONFIGS["debug_user_id"])


def get_market_group_link() -> str:
    return str(GLOBAL_CONFIGS["links"]["market_group_link"])
