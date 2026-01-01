# Handles API interactions.

import requests
from utils.config import BASE_URL

def create_user(user_data):
    return requests.post(f"{BASE_URL}/users", json=user_data)

def get_user(user_id):
    return requests.get(f"{BASE_URL}/users/{user_id}")

def delete_user(user_id):
    return requests.delete(f"{BASE_URL}/users/{user_id}")
