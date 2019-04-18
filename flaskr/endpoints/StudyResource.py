from flask import request, jsonify, current_app, redirect
from flask_restful import Resource
from bson import ObjectId
import json, datetime

from ..db import get_db
from ..entities.User import User


class StudyResource(Resource):
    def get(self):
        # Check authentication
        # auth_header = request.headers.get('Authorization')
        # user_id = User.validate_request(auth_header)
        # if not user_id :
        #     return redirect('/auth', 401)

        if request.args.get('id'):
            return jsonify(study=
                           self.get_study(request.args.get('id')))

        return jsonify(studies=self.load_studies())

    def post(self):
        req = request.json
        args = request.args

        if args.get('title'):
            if not check_title(req.title):
                return jsonify(isValid=False), 409
            else:
                return jsonify(isValid=True), 200

        date = datetime.datetime.now().isoformat()
        # Create the object
        study = {
            'title': req['title'],
            'description': req['description'],
            'cards': req['cards'],
            'message': req['message'],
            'abandonedNo': 0,
            'completedNo': 0,
            'editDate': date,
            'isLive': True,
            'launchedDate': date
        }
        # Save to db
        self.create_study(study)

        # Create the response
        res = {
            'id': date,
            'title': req['title'],
            'abandonedNo': 0,
            'completedNo': 0,
            'editDate': date,
            'isLive': True,
            'launchedDate': date
        }

        return jsonify(study=res)

    def delete(self):
        pass

    @staticmethod
    def create_study(obj):
        with current_app.app_context():
            db = get_db()
        db['studies'].insert_one(obj)

    @staticmethod
    def load_studies():
        with current_app.app_context():
            db = get_db()
        studies = []
        for study in db['studies'].find({}, {
                                                    '_id': 1,
                                                    'title': 1,
                                                    'abandonedNo': 1,
                                                    'completedNo': 1,
                                                    'editDate': 1,
                                                    'isLive': 1,
                                                    'launchedDate': 1}):
            study['id'] = str(study['_id'])
            study['_id'] = None
            studies.append(study)
        return studies

    @staticmethod
    def get_study(id):
        with current_app.app_context():
            db = get_db()
        study = list(db['studies'].find({'_id': ObjectId(id)}))[0]
        study['id'] = str(study['_id'])
        study['_id'] = None
        study['launched'] = study['launchedDate']
        study['launchedDate'] = None
        return study
