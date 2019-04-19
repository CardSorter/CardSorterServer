import os

from flask import Flask
from flask_cors import CORS

from flaskr.InitializeEndpoints import InitializeEndpoints


test_config = None

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


# Endpoints
InitializeEndpoints(app)

#app.run()

