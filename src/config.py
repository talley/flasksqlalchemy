import os

basedir = os.path.abspath(os.path.dirname(__file__))


SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:Iamsmart27@localhost:5432/northwind"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
