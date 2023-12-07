import json
from typing import Any, Generator
from bs4 import BeautifulSoup, ResultSet, Tag
import requests
import hashlib
import urllib.parse

from db_api import add_hotel_hash, create_table

url = 'https://www.sunwing.ca/en/promotion/packages/last-minute-vacations/from-calgary'
API_link = 'https://api.telegram.org/bot5522301142:AAFpmTT9UiFrqcYibr1F7Mied5CTIRqBWF0'


def get_request(url):
    resp = requests.get(url)

    if resp.status_code == 200:
        # with open('index.html', 'w', encoding='utf-8') as file:
        #     file.write(resp.text)
        return resp.text


def make_hotels_list(soup: BeautifulSoup) -> Generator:
    travel_deals: Tag = soup.find('div', attrs={'id': 'travel-deals'})
    hotel_cards: ResultSet[Any] = travel_deals.find_all(
        'div', attrs={'class': 'Grid-module--grid__item--voOrq'})
    for card in hotel_cards:
        heading_module = card.find(
            'h3', attrs={'class': 'Heading-module--heading--h5--3c7Iw'})
        hotel_detail_days = card.find(
            'div', class_='Hotel-module--hotelDetailsDays--1_9lF')
        date, days, conditions = [
            item.text for item in hotel_detail_days.children]
        yield {
            'destination': heading_module.span.text.strip(),
            'title': heading_module.div.text.strip(),
            'rating': card.find('div', class_="StarRating-module--rating--2P6IC")['rating'],
            'date': date,
            'days': days,
            'conditions': conditions,
            'price': card.find('span', class_='Hotel-module--hotelDetailsAmount--2oExH').text.replace('$', '').strip(),
            'image': card.find('div', class_='CardImage-module--image--18emS').picture.img['src'],
            'link': card.find('a', class_='CardBuilder-module--cardLink--uva-c')['href'],
        }


def make_hash(hotel_card: dict) -> str:
    dhash = hashlib.md5()
    encoded = json.dumps(hotel_card, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def make_msg_for_tg(hotel: dict):
    return (
        f'{hotel["destination"]}\n\n'
        f'{hotel["title"]}\n'
        f'rating: {hotel["rating"]}\n\n'
        f'{hotel["date"]}\n'
        f'{hotel["days"]}\n'
        f'{hotel["conditions"]}\n\n'
        f'${hotel["price"]}\n\n'
        # f'{hotel["image"]}'
        f'{hotel["link"]}'
    )


def send_msg_in_tg(msg):
    resp = requests.get(
        API_link +
        f'/sendMessage?chat_id=234043544&text={urllib.parse.quote(msg)}'
    )
    return resp.status_code


def main():
    create_table()
    with open('index.html') as file:
        data = file.read()

    soup = BeautifulSoup(data, 'lxml')
    for hotel in make_hotels_list(soup):
        # print(make_hash(hotel))
        add_hotel_hash(make_hash(hotel))
        status = send_msg_in_tg(make_msg_for_tg(hotel))
        if status != 200:
            print('error')

        break


if __name__ == '__main__':
    main()
