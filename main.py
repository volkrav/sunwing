import json
from typing import Any, Generator
from bs4 import BeautifulSoup, ResultSet, Tag
import requests
import hashlib
import urllib.parse
from datetime import datetime

from db_api import add_offer_hash, create_table

url = 'https://www.sunwing.ca/page-data/en/promotion/packages/last-minute-dominican-republic-vacations/page-data.json'

API_link = 'https://api.telegram.org/bot5522301142:AAFpmTT9UiFrqcYibr1F7Mied5CTIRqBWF0'


def get_json_from_api(url):
    try:
        resp = requests.get(url)
    except Exception as err:
        send_msg_in_tg(
            f'got an error in the "get_json_from_api": {err}')
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
    day = date.day
    month = date.month
    format_date = datetime.strftime(date, "%b %d, %Y %A")
    if (month == 12 and day >= 14) or (month == 1 and day < 10):
        print(day, month)
    else:
        print(f'\t NOO {day}, {month}')
    return (
        f'from: {offer["gateway"]}\n\n'
        f'to: {offer["destination"]}\n\n'
        f'{offer["title"]}\n'
        f'rating: {offer["rating"]}\n\n'
        f'{format_date}\n'
        f'{offer["days"]}\n'
        f'{offer["conditions"]}\n\n'
        f'${offer["price"]}\n\n'
        f'{offer["link"]}'
    )


def checking_compliance(offer: dict) -> bool:
    date = datetime.strptime(offer["date"], '%Y-%m-%dT%H:%M:%S').date()
    return offer['price'] < 1650 and ((date.month == 12 and date.day >= 14) or (date.month == 1 and date.day < 10))


def send_msg_in_tg(msg):
    resp = requests.get(
        API_link +
        f'/sendMessage?chat_id=234043544&text={urllib.parse.quote(msg)}'
    )
    return resp.status_code


def main():
    # create_table()
    # with open('index.html') as file:
    #     data = file.read()

    # soup = BeautifulSoup(data, 'lxml')

    # for hotel in make_hotels_list(soup):
    #     # print(make_hash(hotel))
    #     add_hotel_hash(make_hash(hotel))
    #     status = send_msg_in_tg(make_msg_for_tg(hotel))
    #     if status != 200:
    #         print('error')

    #     break
    for offer in make_offers_list(get_json_from_api(url)):
        print(make_hash(offer))
        # if checking_compliance(offer):
            # send_msg_in_tg(make_msg_for_tg(offer))
        # print(offer)
        break


if __name__ == '__main__':
    main()
