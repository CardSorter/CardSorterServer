from flask import request, jsonify, make_response
from flask_restful import Resource

from flaskr.entities.Study import Study
from flaskr.entities.Participant import Participant
from flaskr.stats.Stats import update_stats


class CardSorterResource(Resource):
    def get(self):
        """
        Sends the details used for the card sort of a study.
        There is one *error* that is returned:
            -STUDY NOT FOUND
        Default case:
            The id must be passed as a parameter, the cards parameter must be true.
            Returns the cards of the study.
        """
        study_id = get_id(request)
        if isinstance(study_id, dict) and study_id['error']:
            return make_response(jsonify(error={'message': 'STUDY NOT FOUND'}), 404)

        if request.args.get('cards'):
            study = Study()
            cards = study.get_cards(study_id)

            if isinstance(cards, dict) and cards['message']:
                return make_response(jsonify(error=cards), 404)

            return jsonify(cards=cards)

    def post(self):
        """
        Submits the sorting of a study.
        There is one *error* that is returned:
            -STUDY NOT FOUND
        Default case:
            The body of the request must consist of the fields: studyID, categories, container, time, comment.
            The thanks message is returned.
        """
        study_id = request.json['studyID']
        categories = request.json['categories']
        non_sorted = request.json['notSorted']
        try:
            time = request.json['time']
        except KeyError:
            time = 'N/A'

        try:
            comment = request.json['comment']
        except KeyError:
            comment = ''

        participant = Participant()

        error = participant.post_categorization(study_id, categories, non_sorted, time, comment)

        if error:
            return jsonify(error=error)

        study = Study()
        print('Updating stats for: ', study_id)
        update_stats(study_id)
        return jsonify(study.get_thanks_message(study_id))

    def delete(self):
        pass


def get_id(req):
    if not req.args.get('study_id') or len(req.args.get('study_id')) == 0 or req.args.get('study_id') == 'null':
        return {'error': 404}
    return req.args.get('study_id')


# def convert_to_date(ms):
# from datetime import timedelta
# return str(timedelta(milliseconds=ms))
#     millis = ms
#     seconds = (millis / 1000) % 60
#     seconds = int(seconds)
#     minutes = (millis / (1000 * 60)) % 60
#     minutes = int(minutes)
#     hours = (millis / (1000 * 60 * 60)) % 24
#     hours = int(hours)
#
#     time = ''
#     if hours > 0:
#         time += str(hours) + ' h '
#     if minutes > 0:
#         time += str(minutes) + ' m '
#     time += str(seconds) + ' s'
#     return time
