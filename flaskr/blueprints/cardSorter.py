import os

from flask import Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound

card_sorter = Blueprint('card_sorter', __name__, static_folder='../public/card_sorter/',
                        template_folder='../public/card_sorter/')


@card_sorter.route('/sort', defaults={'path': ''})
@card_sorter.route('/sort/<path:path>')
def show(path):
    print('Hello')
    try:
        # https://stackoverflow.com/questions/30620276/flask-and-react-routing
        path_dir = os.path.abspath("./public/card_sorter/sorter/build/")  # path react build
        print(path_dir)
        print('with path:', path)
        if path != "" and os.path.exists(os.path.join(path_dir, path)):
            return send_from_directory(os.path.join(path_dir), path)
        else:
            return send_from_directory(os.path.join(path_dir), 'index.html')
        # return render_template('index.html')
    except TemplateNotFound:
        abort(404)
