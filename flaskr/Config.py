import os


class Config:
    host = 'localhost'
    # Real production ip
    # url = 'http://83.212.97.237'
    # Production URL
    # url = 'http://cardsorter.tk'
    # Development URL
    url = os.environ.get('APP_IP', 'http://localhost:3000')
    port = 27017
