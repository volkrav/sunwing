import requests
import urllib.parse
from config import BOT_TOKEN, USERS_ID

API_link = f'https://api.telegram.org/bot{BOT_TOKEN}'


def send_msg_in_tg(msg: str, user_id: str = USERS_ID[0]):
    resp = requests.get(
        API_link +
        f'/sendMessage?chat_id={user_id}&text={urllib.parse.quote(msg)}'
    )
    return resp.status_code
