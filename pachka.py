import os
import re
import requests
from dotenv import load_dotenv

# получим переменные окружения из .env
# load_dotenv()

class Pachka:
    # получим переменные окружения
    USER_ID = "400040"
    ACCESS_TOKEN = "llSvnSFhu7nZTTM3w_nMTY_EKNynw6d0ODV4UcF8s0I"
    INPUT_WEBHOOKS_URL = "https://api.pachca.com/webhooks/01J0RVB229RDQRKYDGB020J6FM"
    API_URL = "https://api.pachca.com/api/shared/v1"
    # CHAT_ID = "12799842"

    def send_response(self,user_id, chat_id,content):
        headers = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }

        data = {
            "message": {
                "user_id": user_id,
                "entity_id": chat_id,
                "content": content,
            }
        }

        post_response = requests.post(f"{self.API_URL}/messages", headers=headers, json=data)
        post_response_json = post_response.json()

        return post_response_json