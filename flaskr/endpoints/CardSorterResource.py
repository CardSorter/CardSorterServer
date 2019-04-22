from flask import request, jsonify, make_response
from flask_restful import Resource

from flaskr.entities.Study import Study
from flaskr.entities.Participant import Participant


class CardSorterResource(Resource):

    def get(self):

        study_id = get_id(request)
        if isinstance(study_id, dict) and study_id['error']:
            return make_response(jsonify(error={'message': 'STUDY NOT FOUND'}), 404)

        if request.args.get('cards'):
            study = Study()
            cards = study.get_cards(study_id)

            if isinstance(cards, dict) and cards['error']:
                return make_response(jsonify(error=cards), 404)

            return jsonify(cards=cards)

    def post(self):
        study_id = request.json['studyID']
        categories = request.json['categories']
        non_sorted = request.json['container']

        participant = Participant()

        error = participant.post_categorization(study_id, categories, non_sorted)

        if error:
            return jsonify(error=error)

        study = Study()
        return jsonify(study.get_thanks_message(study_id))

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
        return {'error': 404}
    return request.args.get('study_id')
