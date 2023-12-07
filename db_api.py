from DB_cm import UseDataBase


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
        print(e)

def add_hotel_hash(hash):
    statement = (
        f'insert into hashes (hash) values=?', (hash, )
    )
    try:
        with UseDataBase() as cursor:
            cursor.execute(statement)
    except Exception as e:
        print(e)
