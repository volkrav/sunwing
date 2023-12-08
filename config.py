from environs import Env

env = Env()
env.read_env()

USERS_ID = env.list('USERS_ID')
BOT_TOKEN = env.str('BOT_TOKEN')
MAX_PRICE = env.int('MAX_PRICE')
DAY_IN_DEC = env.int('DAY_IN_DEC')
DAY_IN_JAN = env.int('DAY_IN_JAN')
