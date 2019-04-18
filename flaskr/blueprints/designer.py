import os

from flask import Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound

designer = Blueprint('designer', __name__, static_folder='../public/card_sorter/',
                     template_folder='../public/card_sorter/')


@designer.route('/', defaults={'path': ''})
@designer.route('/<path:path>')
def show(path):
    try:
        # https://stackoverflow.com/questions/30620276/flask-and-react-routing
        path_dir = os.path.abspath("./public/card_sorter/designer/build")  # path react build
        print('Its a me')
        if path != "" and os.path.exists(os.path.join(path_dir, path)):
            return send_from_directory(os.path.join(path_dir), path)
        else:
            return send_from_directory(os.path.join(path_dir), 'index.html')
    except TemplateNotFound:
        abort(404)
