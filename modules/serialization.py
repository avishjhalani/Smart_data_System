import json
import os

FILE_PATH = "data/users.json"

def load_users():
    if not os.path.exists(FILE_PATH):
        return []
    
    with open(FILE_PATH, "r") as f:
        return json.load(f)


def save_user(user):
    users = load_users()
    users.append(user)

    with open(FILE_PATH, "w") as f:
        json.dump(users, f, indent=4)
        