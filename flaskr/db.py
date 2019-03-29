
from flask import current_app, g
import pymysql

from flaskr.Config import Config


def get_db():
    conn = pymysql.connect(host=Config.host, user=Config.user, password=Config.password, db=Config.database
                           , cursorclass=pymysql.cursors.DictCursor)
    # if 'db' not in g:
    #     g.db = pymysql.connect(current_app.config['DATABASE'], cursorclass=pymysql.cursors.DictCursor)

    print('Connected to database.')
    return conn


def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()
