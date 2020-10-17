from pymongo import MongoClient
from flask import g
from flaskr.Config import Config
import os


def get_db():
    if 'db' not in g:
        db_username = os.environ.get('MONGODB_USERNAME', 'rest_api')
        db_password = os.environ.get('MONGODB_PASSWORD', 'example')
        db_host = os.environ.get('MONGODB_HOSTNAME', '127.0.0.1')
        db_database = os.environ.get('MONGODB_DATABASE', 'card_sorter')
        mongoURI = 'mongodb://' + db_username + ':' + db_password + '@' + db_host + ':27017/' + db_database

        conn = MongoClient(mongoURI, authSource=str(db_database))
        g.conn = conn
        g.db = conn[db_database]


    return g.db
