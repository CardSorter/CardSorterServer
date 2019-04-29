from flask import request, jsonify, make_response
from flask_restful import Resource

from flaskr.entities.Study import Study
from flaskr.entities.Participant import Participant
from flaskr.stats.Stats import update_stats


class CardSorterResource(Resource):

    def get(self):

        study_id = get_id(request)
        if isinstance(study_id, dict) and study_id['error']:
            return make_response(jsonify(error={'message': 'STUDY NOT FOUND'}), 404)

        if request.args.get('cards'):
            study = Study()
            cards = study.get_cards(study_id)

            print(cards)
            if isinstance(cards, dict) and cards['message']:
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
        update_stats(study_id)
        return jsonify(study.get_thanks_message(study_id))

    def delete(self):
        pass


def get_id(req):
    if not req.args.get('study_id') or len(req.args.get('study_id')) == 0 or req.args.get('study_id') == 'null':
        return {'error': 404}
    return req.args.get('study_id')
