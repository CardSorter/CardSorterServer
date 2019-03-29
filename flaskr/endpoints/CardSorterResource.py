from flask import request, jsonify, json
from flask_restful import Resource

class CardSorterResource(Resource):

    def get(self):

        if not request.args.get('study_id'):
            return 'Study id not set', 400
        study_id = request.args.get('study_id')

        if request.args.get('cards'):
            cards = getCards(study_id)
            return jsonify(cards=cards)

    def post(self):
        pass

    def delete(self):
        pass


def getCards(study_id: int):
    cards = []
    for i in range(0, 20):
        cards.append({
                'id': i,
                'title': 'Card' + str(i),
                'description': 'Lorem ipsum sit dolor',
            })
    return cards

