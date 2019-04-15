from flask import request, jsonify
from flask_restful import Resource
import json, datetime


class StudyResource(Resource):

    def get(self):
        if request.args.get('id'):
            return jsonify(study=
                           get_study(request.args.get('id')))

        return jsonify(studies=load_studies())

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


def get_study(id: int):
    date = datetime.datetime.now().isoformat()
    return {
        'id': id,
        'title': 'Title',
        'isLive': True,
        'launched': date,
        'participants': {
            'completion': '50%',
            'total': 99,
            'completed': 49,
            'data': [
                ['#1', '00:05:43', '100%', '6'],
                ['#2', '00:05:43', '100%', '6'],
                ['#3', '00:05:43', '100%', '6'],
                ['#4', '00:05:43', '100%', '6'],
                ['#5', '00:05:43', '100%', '6'],
                ['#6', '00:05:43', '100%', '6'],
                ['#7', '00:05:43', '100%', '6'],
                ['#8', '00:05:43', '100%', '6'],
                ['#9', '00:05:43', '100%', '6'],
                ['#10', '00:05:43', '100%', '6'],
                ['#11', '00:05:43', '100%', '6'],
            ],
        },
        'cards': {
            'average': '60%',
            'total': 100,
            'sorted': 60,
            'data': [
                ['Card1', 4, 'Category1', 2],
                ['Card2', 4, 'Category1', 2],
                ['Card3', 4, 'Category1', 2],
                ['Card4', 4, 'Category1', 2],
                ['Card5', 4, 'Category1', 2],
                ['Card6', 4, 'Category1', 2],
                ['Card7', 4, 'Category1', 2],
            ],
        },
        'categories': {
            'similarity': '20%',
            'total': 20,
            'similar': 100,
            'merged': 2,
            'data': [
                ['Category1', 3, 'Card1', 4, 4],
                ['Category2', 3, 'Card1', 4, 4],
                ['Category3', 3, 'Card1', 4, 4],
                ['Category4', 3, 'Card1', 4, 4],
                ['Category5', 3, 'Card1', 4, 4],
                ['Category6', 3, 'Card1', 4, 4],
                ['Category7', 3, 'Card1', 4, 4],
            ],
        }
    }
