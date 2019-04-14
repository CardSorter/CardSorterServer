from flask import request, jsonify
from flask_restful import Resource
import json, datetime
from collections import namedtuple


class StudyResource(Resource):

    def get(self):
        return jsonify(studies=load_studies())

    def post(self):
        req = request.json
        # Parse JSON into an object with attributes corresponding to dict keys.
        # req = json.loads(req, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        # req = json.loads(req)
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
            'url': req['url'],
            'cards': req['cards'],
            'message': req['message'],
            'abandonedNo': 0,
            'completedNo': 0,
            'editDate': date,
            'isLive': True,
            'launcedDate': date
        }

        # Create the response
        res = {
            'id': date,
            'title': req['title'],
            'abandonedNo': 0,
            'completedNo': 0,
            'editDate': date,
            'isLive': True,
            'launcedDate': date
        }

        return jsonify(study=res)

    def delete(self):
        pass


def load_studies():
    studies = []
    date = datetime.datetime.now().isoformat()
    for i in range(0, 20):
        studies.append({
            'id': i,
            'title': 'Study #' + str(i),
            'abandonedNo': 3,
            'completedNo': 48,
            'editDate': date,
            'endDate': date,
            'isLive': True if i % 3 == 0 else False,
            'launcedDate': date})
    return studies


def check_title(title):
    return False
