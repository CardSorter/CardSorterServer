from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

card_sorter = Blueprint('card_sorter', __name__, static_folder='./static/card_sorter/build/static',
                        template_folder='../static/card_sorter/build')


@card_sorter.route('/sort')
def show():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)

