import json
import os
import sys

GLOBAL_CONFIGS = {}


def load_configs() -> dict:
    path = "/configs/deploy.json" if sys.argv[1] == "deploy" else "configs/debug.json"
    with open(os.path.abspath(path)) as f:
        return json.load(f)


def get_bot_username() -> str:
    return GLOBAL_CONFIGS["bot_username"]


def get_main_id() -> int:
    return int(GLOBAL_CONFIGS["groups_info"]["main_id"])


def get_market_id() -> int:
    return int(GLOBAL_CONFIGS["groups_info"]["market_id"])


def get_approval_id() -> int:
    return int(GLOBAL_CONFIGS["groups_info"]["approval_id"])


def get_feedback_channel_id() -> int:
    return int(GLOBAL_CONFIGS["channel_info"]["feedback_id"])


def get_logging_channel_id() -> int:
    return int(GLOBAL_CONFIGS["channel_info"]["logging_id"])


def get_roles() -> list[str]:
    return GLOBAL_CONFIGS["roles"]


def get_debug_user_id() -> int:
    return int(GLOBAL_CONFIGS["debug_user_id"])


def get_max_username_length() -> int:
    return int(GLOBAL_CONFIGS["global_variables"]["max_username_length"])


def get_market_group_link() -> str:
    return GLOBAL_CONFIGS["links"]["market_group_link"]
