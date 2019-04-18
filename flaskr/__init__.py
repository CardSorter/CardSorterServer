import os

from flask import Flask
from flask_cors import CORS

from flaskr import db
from .blueprints.designer import designer
from .blueprints.auth import auth
from .blueprints.cardSorter import card_sorter
from flaskr.InitializeEndpoints import InitializeEndpoints


def create_app(test_config=None):

    # Configuration
    app = Flask(__name__, instance_relative_config=True, static_folder='./public/card_sorter/',
                template_folder="./public/card_sorter/")
    app.config.from_mapping(
        SECRET_KEY='development',
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

    # Route: /auth
    app.register_blueprint(auth)

    # Route: /sort
    app.register_blueprint(card_sorter)

    # Route: /
    app.register_blueprint(designer)

    # Endpoints
    InitializeEndpoints(app)

    return app


create_app().run()
