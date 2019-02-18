import os

from flask import Flask

from flaskr import db


def create_app(test_config=None):

    # Configuration
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    database = db.DB()

    @app.route('/')
    def hello():
        return 'It is alive!'

    return app


create_app().run()
