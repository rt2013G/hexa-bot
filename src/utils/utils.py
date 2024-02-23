from src.utils.config import get_market_id, get_main_id, get_approval_id

def is_admin(user_id) -> bool:
    pass

def is_market_group(chat_id) -> bool:
    return chat_id == get_market_id()

def is_main_group(chat_id) -> bool:
    return chat_id == get_main_id()

def is_approval_group(chat_id) -> bool:
    return chat_id == get_approval_id