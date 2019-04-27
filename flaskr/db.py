from pymongo import MongoClient
from flask import g
from flaskr.Config import Config


def get_db():
    if 'db' not in g:
        conn = MongoClient(Config.host, Config.port)
        g.conn = conn
        g.db = conn['card_sorter']

    return g.db
