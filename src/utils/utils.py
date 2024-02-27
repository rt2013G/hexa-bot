from src.database.dbms import get_role_list
from src.config import get_roles

def is_role(user_id: int, role_name: str) -> bool:
    if role_name not in get_roles():
        return False
    id_list = []
    for user in get_role_list(role_name):
        id_list.append(user.id)
    return user_id in id_list
