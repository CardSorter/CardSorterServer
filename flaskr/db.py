
from flask import current_app, g
import pymysql


def get_db_cursor():
    # Configuration
    # user = 'server_connection'
    # password = '1234'
    # database = 'sampleDB'
    # host = 'localhost'
    # conn = pymysql.connect(host=host, user=user, password=password, db=database
    #                        , cursorclass=pymysql.cursors.DictCursor)

    if 'db' not in g:
        g.db = pymysql.connect(current_app.config['DATABASE'], cursorclass=pymysql.cursors.DictCursor)

    print('Connected to database.')
    return g.db


def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()
