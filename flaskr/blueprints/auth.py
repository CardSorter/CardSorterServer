import os

from flask import Blueprint, send_from_directory

auth = Blueprint('auth', __name__, static_folder='../public/card_sorter/',
                 template_folder='../public/card_sorter/')


@auth.route('/auth', defaults={'path': ''})
@auth.route('/auth/<path:path>')
def show(path):
    # https://stackoverflow.com/questions/30620276/flask-and-react-routing
    path_dir = os.path.abspath("./public/card_sorter/auth/build/")  # path react build
    if path != "" and os.path.exists(os.path.join(path_dir, path)):
        return send_from_directory(os.path.join(path_dir), path)
    else:
        return send_from_directory(os.path.join(path_dir), 'index.html')
