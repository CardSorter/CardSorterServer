import os

from flask import Flask
from flask_cors import CORS


from flaskr.InitializeEndpoints import InitializeEndpoints
from flaskr.db import get_db

# Configuration
# application = Flask(__name__, instance_relative_config=True)
application = Flask(__name__)

application.config.from_mapping(
    # change this on deployment only
    SECRET_KEY='development',
)

CORS(application, supports_credentials=True)

application.config.from_pyfile('./flaskr/Config.py', silent=True)

# Ensure the instance folder exists
try:
    os.makedirs(application.instance_path)
except OSError:
    print('!Instance folder does not exist!')
    pass

# Endpoints
InitializeEndpoints(application)

if __name__ == '__main__':
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
