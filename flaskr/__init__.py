import os

from flask import Flask
from flask_cors import CORS
from flaskr.db import get_db


from flaskr.InitializeEndpoints import InitializeEndpoints

# Configuration
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    # change this on deployment only
    SECRET_KEY='development',
)
CORS(app, supports_credentials=True)

app.config.from_pyfile('Config.py', silent=True)

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Endpoints
InitializeEndpoints(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
