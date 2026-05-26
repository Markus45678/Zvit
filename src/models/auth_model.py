import json
import os.path


def authenticate(username, password):

    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_path, "storages", "users.json")

    if not os.path.exists(db_path):
        return None

    with open(db_path, "r", encoding="utf-8") as f:
        users = json.load(f)

    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None