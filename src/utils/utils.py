from src.database.dbms import get_role_list

def is_admin(user_id) -> bool:
    id_list = []
    for user in get_role_list("admin"):
        id_list.append(user.id)
    return user_id in id_list
