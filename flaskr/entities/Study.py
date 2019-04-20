import datetime

from bson import ObjectId
from flask import current_app

from flaskr.db import get_db


class Study:
    def __init__(self):
        with current_app.app_context():
            self.users = get_db()['users']
            self.studies = get_db()['studies']
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
        return study

    def _post_study(self, study):
        item = self.studies.insert_one(study)
        self.study_id = ObjectId(item.inserted_id)
