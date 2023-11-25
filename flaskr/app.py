import os

from flask import Flask
from flask_cors import CORS


from flaskr.InitializeEndpoints import InitializeEndpoints

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
    ENVIRONMENT_HOST = os.environ.get("APP_HOST", '127.0.0.1')
    application.run(host=ENVIRONMENT_HOST, port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
