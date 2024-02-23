import os
import sys
import json

GLOBAL_CONFIGS = None

def load_configs() -> dict:
    path = "/configs/deploy.json" if sys.argv[1] == "deploy" else "configs/debug.json"
    with open(os.path.abspath(path)) as f:
        return json.load(f)
    
def get_bot_tag() -> str:
    return GLOBAL_CONFIGS["bot_tag"]

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
    