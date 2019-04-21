import datetime

from bson import ObjectId
from flask import current_app

from flaskr.db import get_db


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
            'launchedDate': date
        }
        self._post_study(study)
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

        # Make the json array specified
        # data: 0: participant id 1: time taken 2: cards sorted 3: categories created
        participants = []
        no = 1
        for participant_id in study['participants']:
            participant = list(self.participants.find({'_id': participant_id},
                                                      {'_id': 0, 'cards_sorted': 1, 'categories_no': 1}))[0]
            participants.append([no, 'N/A', participant['cards_sorted'], participant['categories_no']])
            no += 1

        # Calculate completion
        total = len(study['participants'])
        completed = len(list(self.participants.find({'cards_sorted': '100%'})))

        # Make full json structure

        study['participants'] = {
            'completion': str(int(completed/total * 100)) + '%',
            'total': total,
            'completed': completed,
            'data': participants
        }

        print(study)
        return study

    def get_cards(self, study_id):
        study = list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'cards': 1}))[0]
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
