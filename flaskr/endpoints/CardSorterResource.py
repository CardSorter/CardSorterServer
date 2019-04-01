from flask import request, jsonify
from flask_restful import Resource


class CardSorterResource(Resource):

    def get(self):
        study_id = get_id(request)
        if request.args.get('cards'):
            cards = get_cards(study_id)
            return jsonify(cards=cards)

    def post(self):
        print(request.json)

    def delete(self):
        pass


def get_cards(study_id: int):
    cards = []
    for i in range(0, 20):
        cards.append({
                'id': i,
                'title': 'Card' + str(i),
                'description': 'Lorem ipsum sit dolor',
            })
    return cards


def get_id(request):
    if not request.args.get('study_id'):
        return 'Study id not set', 400
    return request.args.get('study_id')
