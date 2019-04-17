import os

from flask import Flask
from flask_cors import CORS

from flaskr import db
from .blueprints.cardSorter import card_sorter
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

    # First level API

    @app.route('/')
    def hello():
        return 'Work in progress'

    # Route: /sort
    app.register_blueprint(card_sorter)

    # Endpoints
    InitializeEndpoints(app)

    return app


create_app().run()
