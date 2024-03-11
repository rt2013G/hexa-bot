import json
import os
from datetime import datetime


def load_configs() -> dict:
    path = "app/static/deployment_config.json"
    if not os.path.exists(os.path.abspath(path)):
        path = "app/static/debug_config.json"
    with open(os.path.abspath(path), "r") as f:
        return dict(json.load(f))


GLOBAL_CONFIGS: dict = load_configs()


def get_bot_username() -> str:
    return str(GLOBAL_CONFIGS["bot_username"])


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


def get_debug_user_id() -> int:
    return int(GLOBAL_CONFIGS["debug_user_id"])


def get_market_group_link() -> str:
    return str(GLOBAL_CONFIGS["links"]["market_group_link"])


def get_default_post_datetime() -> datetime:
    return datetime(year=2015, month=1, day=15)


def get_max_data_cache_size() -> int:
    return int(GLOBAL_CONFIGS["global_variables"]["max_card_data_cache_size"])
