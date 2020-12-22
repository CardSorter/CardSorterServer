import os


class Config:
    host = 'localhost'
    url = os.environ.get('APP_IP', 'http://localhost:3000/')
    port = 27017
