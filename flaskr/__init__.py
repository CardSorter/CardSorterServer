import os

from flask import Flask, render_template
from flask_restful import Resource, Api
from flask_cors import CORS

from flaskr import db
from . import auth
from flaskr.InitializeEndpoints import InitializeEndpoints


def create_app(test_config=None):

    # Configuration
    app = Flask(__name__, instance_relative_config=True, static_folder='./static/card_sorter/build/static',
                template_folder="./static/card_sorter/build")
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    CORS(app)

    if test_config is None:
        app.config.from_pyfile('Config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    database = db.get_db()

    app.register_blueprint(auth.bp)

    # First level API

    @app.route('/')
    def hello():
        return 'Work in progress'

    @app.route('/sort')
    def serve_card_sorter():
        return render_template('index.html')

    # Endpoints
    endpoints = InitializeEndpoints(app, database)

    return app


create_app().run()
