import requests
from config.settings import BOT_TOKEN, CHAT_ID

def send_telegram(message, parse_mode=None):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    if parse_mode:
        data["parse_mode"] = parse_mode

    requests.post(url, data=data)