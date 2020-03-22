import datetime
from peewee import *
from playhouse.migrate import *
from .config import DB_NAME, DB_USER, DB_HOST, DB_PSWD, DATABASE_URL, db


class BaseModel(Model):

    utime = DateTimeField(default=datetime.datetime.now())
    ctime = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db
        legacy_table_names = False


class User(BaseModel):

    email = CharField(max_length=256, unique=True)
    level = SmallIntegerField(default=1)  # 1 - 4
    points = IntegerField(default=0)
    is_active = BooleanField(default=True)
    # client | staff
    user_type = CharField(max_length=256, default='client')


class Login(BaseModel):

    user = ForeignKeyField(User, backref='logins')
    pin = IntegerField(null=True)
    device = TextField(null=True)
    token = CharField(max_length=512, null=True)
    duration = SmallIntegerField(default=30, null=True)


class Entry(BaseModel):

    entry = TextField()
    level = SmallIntegerField()  # -> 1 - 4
    is_locked = BooleanField(default=False)
    is_translated = BooleanField(default=False)


class Translation(BaseModel):

    user = ForeignKeyField(User, backref="user_trans")
    entry = ForeignKeyField(Entry, backref="trans")
    translation = TextField()
    passed = SmallIntegerField(default=0)
    failed = SmallIntegerField(default=0)


class Validation(BaseModel):

    user = ForeignKeyField(User, backref="user_valids")
    translation = ForeignKeyField(Translation, backref="valids")
    rating = SmallIntegerField()


class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        db.connect()

    def process_response(self, req, resp, resource, req_succeeded):
        if not db.is_closed():
            db.close()


DataBaseMappings = {
    'user': User,
    'entry': Entry,
    'translation': Translation,
    'validation': Validation
}

if __name__ == "__main__":
    import sys

    def up():
        db.create_tables([
            User, Login, Entry, Translation, Validation,
        ])

    def down():
        db.drop_tables([
            User, Login, Entry, Translation, Validation,
        ])

    try:
        if sys.argv[1] == "+":
            up()
            print("Successfully created tables ...")
        elif sys.argv[1] == "-":
            down()
            print("Successfully dropped tables ...")
        elif sys.argv[1] == "-+":
            down()
            up()
            print("Successfully reloaded tables ...")
        elif sys.argv[1] == "+-+":
            migrator = PostgresqlMigrator(db)
            migrate(
                # migrator.add_column('entry', 'is_locked', BooleanField(default=False)),
            )
            print('migration successfull')
        else:
            print(f"Could not execute {sys.argv[1]}")
    except Exception as e:
        print(e)
