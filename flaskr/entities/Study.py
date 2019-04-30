import datetime

from bson import ObjectId
from flask import current_app
from math import ceil

from flaskr.db import get_db
from flaskr.stats.Stats import build_similarity_matrix


class Study:
    def __init__(self):
        with current_app.app_context():
            self.users = get_db()['users']
            self.studies = get_db()['studies']
            self.participants = get_db()['participants']
        self.study_id = 0

    def create_study(self, title, description, cards, message, user_id):
        date = datetime.datetime.utcnow()
        study = {
            'title': title,
            'description': description,
            'cards': cards,
            'message': message,
            'abandonedNo': 0,
            'completedNo': 0,
            'editDate': date,
            'isLive': True,
            'launchedDate': date,
            'participants': [],
        }
        self._post_study(study)

        # Create the appropriate fields
        build_similarity_matrix(str(self.study_id))

        # Link study to the user
        self.users.update_one({'_id': ObjectId(user_id)}, {'$push': {'studies': self.study_id}})

    def get_studies(self, user_id):
        study_ids = list(self.users.find({'_id': ObjectId(user_id)}, {'_id': 0, 'studies': 1}))[0]['studies']
        studies = []
        for study_id in study_ids:
            study = list(self.studies.find({'_id': ObjectId(study_id)}, {
                'title': 1,
                'abandonedNo': 1,
                'completedNo': 1,
                'editDate': 1,
                'isLive': 1,
                'launchedDate': 1}))[0]
            study['id'] = str(study['_id'])
            study['_id'] = None
            studies.append(study)
        return studies

    def get_study(self, study_id, user_id):
        # Check if the study belongs to the user
        available_studies = list(self.users.find({'_id': ObjectId(user_id)}, {'_id': 0, 'studies': 1}))[0]['studies']

        if ObjectId(study_id) not in available_studies:
            return {'message': 'INVALID STUDY'}

        study = list(self.studies.find({'_id': ObjectId(study_id)}))[0]
        study['id'] = str(study['_id'])
        study['_id'] = None

        # Make full json structure
        # Calculate participants data

        # Make the json array specified
        # data: 0: participant_no id 1: time taken 2: cards sorted 3: categories created
        participants = []
        no = 1
        try:
            for participant_id in study['participants']:
                participant = list(self.participants.find({'_id': participant_id},
                                                          {'_id': 0, 'cards_sorted': 1, 'categories_no': 1}))[0]
                participants.append(['#' + str(no), 'N/A', str(participant['cards_sorted']) + '%'
                                    , participant['categories_no']])
                no += 1
        except KeyError:
            return {'participants': 0}

        total = len(study['participants'])

        # Return no participants json
        if total == 0:
            return {'participants': 0}

        completed = len(list(self.participants.find({'cards_sorted': 100})))

        study['participants'] = {
            'completion': study['stats']['completion'],
            'total': total,
            'completed': completed,
            'data': participants
        }

        # Calculate cards data

        # Make the json array specified
        # data: 0: card_name 1: categories_no 2: categories names 3: frequency
        cards = []
        for card_id in study['cards']:
            card = study['cards'][card_id]
            try:
                categories = study['cards'][card_id]['categories']
            except KeyError:
                categories = []
            try:
                frequencies = study['cards'][card_id]['frequencies']
            except KeyError:
                frequencies = []
            categories_no = len(categories)
            cards.append([card['name'], categories_no, categories, frequencies])

        study['cards'] = {
            'average': str(study['stats']['average_sort']) + '%',
            'total': total,
            'sorted': int(total * study['stats']['average_sort'] * (1 / 100)),
            'data': cards,
        }

        # Calculate categories data

        # Make the json array specified
        # data: 0: category name 1: cards no 2: cards 3: frequency 4: participants
        categories = []
        for category_name in study['categories']:
            category = study['categories'][category_name]
            categories.append([category_name, len(category['cards']), category['cards'],
                               category['frequencies'], category['participants']])

        study['categories'] = {
            'similarity': '0%',
            'total': len(categories),
            'similar': 0,
            'merged': 0,
            'data': categories,
        }
        study['similarityMatrix'] = self._convert_similarity_matrix(study)

        return study

    @staticmethod
    def _convert_similarity_matrix(study):
        """
        Converts the times each card was found in the same category to the actual percentage.
        This also includes the times that a card was not sorted. Meaning that a card can be sorted with it's self
        less than 100%.
        :param study: the study document
        :return: the similarity matrix
        """
        total_sorts = len(study['participants']['data'])
        card_names = study['stats']['similarities']['card_names']
        similarity_matrix = []
        no = 0
        for line in study['stats']['similarities']['times_in_same_category']:
            for i in range(0, len(line) - 1):
                line[i] = ceil((line[i]/total_sorts) * 100)

            line[len(line) - 1] = card_names[no]
            similarity_matrix.append(line)
            no += 1

        return similarity_matrix

    def get_cards(self, study_id):
        study = list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'cards': 1}))

        if len(study) == 0:
            return {'message': 'STUDY NOT FOUND'}
        study = study[0]

        cards = []
        for card in study['cards'].values():
            cards.append(card)
        return cards

    def get_thanks_message(self, study_id):
        message = list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'message': 1}))[0]
        return message

    def _post_study(self, study):
        item = self.studies.insert_one(study)
        self.study_id = ObjectId(item.inserted_id)
