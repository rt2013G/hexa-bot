from src.database.dbms import get_role_list, get_user_from_id, get_user_from_username
from src.database.model import User
from src.config import get_roles, get_bot_username, get_max_username_length

def get_user_from_message_command(message_text: str, command_text: str) -> User | None:
    msg = remove_bot_username(message_text)
    msg = msg.replace(command_text, "").replace(" ", "")
    if len(msg) > 1 + get_max_username_length():
        return None
    
    if "@" in msg:
        msg = msg.replace("@", "")
        if msg.isnumeric():
            return None
        else:
            return get_user_from_username(username=msg)
    elif msg.isnumeric():
        return get_user_from_id(int(msg))
    
    return None

def is_role(user_id: int, role_name: str) -> bool:
    if role_name not in get_roles():
        return False
    id_list = []
    for user in get_role_list(role_name):
        id_list.append(user.id)
    return user_id in id_list
    
def remove_bot_username(text: str) -> str:
    return text.replace(get_bot_username(), "")
