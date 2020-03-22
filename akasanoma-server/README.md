### Project Setup

pip install requirements.txt

#### Database Migrations (Postgres Database)

- Set up database variables in .env
- Run "~/akasanoma/server$ python3 -m akasanoma.db +" to create all tables
- Run "~/akasanoma/server$ python3 -m akasanoma.db -" to drop all tables
- Run "~/akasanoma/server$ python3 -m akasanoma.db -+" to drop and create


#### Run Project

gunicorn akasanoma.app:api --reload
