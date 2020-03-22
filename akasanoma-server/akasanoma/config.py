from os import getenv
from peewee import PostgresqlDatabase
from dotenv import load_dotenv

load_dotenv()

DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_HOST = getenv("DB_HOST")
DB_PSWD = getenv("DB_PSWD")
SENDGRID_API_KEY = getenv("SENDGRID_API_KEY")
DATABASE_URL = getenv("DATABASE_URL")
TESTING = getenv("TESTING")


if TESTING == 'true':
    db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PSWD, host=DB_HOST)
else:
    from playhouse.db_url import connect
    db = connect(DATABASE_URL)