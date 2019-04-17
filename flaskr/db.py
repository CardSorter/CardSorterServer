from pymongo import MongoClient
from flask import current_app, g
from flaskr.Config import Config


def get_db():
    if 'db' not in g:
        conn = MongoClient(Config.host, Config.port)
        g.db = conn['card_sorter']
        print('Connected to database.')

    return g.db
