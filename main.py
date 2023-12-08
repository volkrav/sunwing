import json
from typing import Generator
import requests
import hashlib
from datetime import datetime
from config import DAY_IN_DEC, DAY_IN_JAN, MAX_PRICE, USERS_ID

from db_api import add_offer_hash, create_table, does_offer_exist
from utils import send_msg_in_tg

url = 'https://www.sunwing.ca/page-data/en/promotion/packages/last-minute-dominican-republic-vacations/page-data.json'


def get_json_from_api(url):
    try:
        resp = requests.get(url)
    except Exception as err:
        send_msg_in_tg(
            f'got an error in the "get_json_from_api": {err.args[0]}')
        exit(1)
    if resp.status_code == 200:
        return resp.json()
    else:
        send_msg_in_tg(
            f'got an error in the "get_json_from_api": status_code {resp.status_code}')
        return


def make_offers_list(json_from_api: dict) -> Generator:
    result = json_from_api['result']['data']['contentfulFluidLayout']['pageSections']['pageSections'][1]['fields']['admodule'][1]
    offers = result['PromotionGroups'][0]['Offers']
    for offer in offers:
        destination = offer['Destination']['Name'] + \
            ', ' + offer['Destination']['CountryName']
        yield {
            'gateway': offer['Gateway']['Name'],
            'destination': destination,
            'title': offer['AccommodationInfo']['AccommodationName'],
            'rating': offer['AccommodationInfo']['StarRating'],
            'date': offer['DepartureDate'],
            'days': offer['Duration'],
            'conditions': offer['MealPlan'],
            'price': offer['Price'],
            'link': offer['DeepLink'],
        }


def make_hash(offer: dict) -> str:
    dhash = hashlib.md5()
    encoded = json.dumps(offer, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def make_msg_for_tg(offer: dict):
    date = datetime.strptime(offer["date"], '%Y-%m-%dT%H:%M:%S').date()
    format_date = datetime.strftime(date, "%b %d, %Y %A")
    return (
        f'from: {offer["gateway"]}\n\n'
        f'to: {offer["destination"]}\n\n'
        f'{offer["title"]}\n'
        f'rating: {offer["rating"]}\n\n'
        f'{format_date}\n'
        f'{offer["days"]} days\n'
        f'{offer["conditions"]}\n\n'
        f'${offer["price"]}\n\n'
        f'{offer["link"]}'
    )


def checking_compliance(offer: dict) -> bool:
    date = datetime.strptime(offer["date"], '%Y-%m-%dT%H:%M:%S').date()
    return offer['price'] < MAX_PRICE and ((date.month == 12 and date.day >= DAY_IN_JAN) or (date.month == 1 and date.day < DAY_IN_JAN))


def main():
    create_table()

    for offer in make_offers_list(get_json_from_api(url)):
        hashed_offer = make_hash(offer)
        if does_offer_exist(hashed_offer):
            continue
        add_offer_hash(hashed_offer)
        if checking_compliance(offer):
            for user_id in USERS_ID:
                send_msg_in_tg(make_msg_for_tg(offer), user_id)


if __name__ == '__main__':
    main()
