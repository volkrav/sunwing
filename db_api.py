from DB_cm import UseDataBase
from utils import send_msg_in_tg


def create_table():
    statement = '''
        CREATE TABLE IF NOT EXISTS hashes (
        id integer PRIMARY KEY,
        hash VARCHAR(255) NOT NULL
        );
        '''
    try:
        with UseDataBase() as cursor:
            cursor.execute(statement)
    except Exception as e:
        send_msg_in_tg("got error in 'create_table' : " + e.args[0])
        exit(1)


def add_offer_hash(hash):
    statement = '''insert into hashes (hash) values(?)'''
    try:
        with UseDataBase() as cursor:
            cursor.execute(statement, (hash,))
    except Exception as e:
        send_msg_in_tg("got error in 'add_offer_hash' : " + e.args[0])
        exit(1)


def does_offer_exist(hashed_offer: str) -> bool:
    try:
        with UseDataBase() as cursor:
            cursor.execute(
                f'select * from hashes where hash=?', (hashed_offer, )
            )
            return cursor.fetchone() != None
    except Exception as e:
        send_msg_in_tg("got error in 'does_offer_exist' : " + e.args[0])
        exit(1)
