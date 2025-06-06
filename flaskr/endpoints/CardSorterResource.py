from flask import request, jsonify, make_response
from flask_restful import Resource

from flaskr.entities.Study import Study
from flaskr.entities.Participant import Participant
from flaskr.stats.Stats import update_stats
from bson import ObjectId


class CardSorterResource(Resource):
    def get(self):
        """
        Sends the details used for the card sort of a study, title and description.
        There is one *error* that is returned:
            - STUDY NOT FOUND
        Default case:
            The ID must be passed as a parameter, and the 'cards' parameter must be true.
            Returns the cards of the study.
        """

        # Get and validate the study ID
        study_id = get_id(request)
        if isinstance(study_id, dict) and study_id.get('error'):
            return {'error': 'STUDY NOT FOUND'}, 404

        # Convert to ObjectId for MongoDB query
        try:
            study_id = ObjectId(study_id)
        except Exception:
            return {'error': 'Invalid study ID'}, 400

        # Handle ?cards=true parameter
        if request.args.get('cards'):
            study = Study()
            cards = study.get_cards(study_id)
            title_desc = study.get_title_description(study_id)

            if isinstance(cards, dict) and cards.get('message'):
                return {'error': cards['message']}, 404

            # Clean and structure card data
            cards_return = []
            for card in cards:
                cards_return.append({
                    'id': card['id'],
                    'name': card['name'],
                    'description': card.get('description', '')
                })

            # Find the study document
            studydocument = study.studies.find_one({'_id': study_id})
            if not studydocument:
                return {'error': 'Study not found'}, 404

            # Get sort type and build response
            sort_type = studydocument.get('sortType', 'open')

            result = {
                'cards': cards_return,
                'title': title_desc['title'],
                'description': title_desc['description'],
                'sortType': sort_type
            }

            # Include predefined categories if closed/hybrid
            if sort_type in ['closed', 'hybrid']:
                result['categories'] = studydocument.get('categories', {})

            print("Returning result:", result)

            return result, 200

        # If 'cards' parameter is missing or invalid
        return {'error': 'Missing or invalid parameters'}



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
        non_sorted = request.json['container']
        new_categories=request.json.get('newCategories', {})  # hybrid sort type
        try:
            time = convert_to_date(request.json['time'])
        except KeyError:
            time = 'N/A'

        try:
            comment = request.json['comment']
        except KeyError:
            comment = ''

        participant = Participant()

        # This is if sort_type=hybrid and create new_categories

        error = participant.post_categorization(study_id, categories, non_sorted, time, comment,new_categories=new_categories)

        if error:
            return jsonify(error=error)

        study = Study()
        print('Updating stats for: ', study_id)
        update_stats(study_id)
        return jsonify(study.get_thanks_message_and_link(study_id))

    def delete(self):
        pass


def get_id(req):
    if not req.args.get('study_id') or len(req.args.get('study_id')) == 0 or req.args.get('study_id') == 'null':
        return {'error': 404}
    return req.args.get('study_id')


def convert_to_date(ms):
    millis = ms
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (millis / (1000 * 60 * 60)) % 24
    hours = int(hours)

    time = ''
    if hours > 0:
        time += str(hours) + ' h '
    if minutes > 0:
        time += str(minutes) + ' m '
    time += str(seconds) + ' s'
    return time
