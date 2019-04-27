from flask import request, jsonify, make_response
from flask_restful import Resource
import datetime

from flaskr.Config import Config
from flaskr.entities.Study import Study
from flaskr.entities.User import User


class StudyResource(Resource):
    def get(self):
        # Check authentication
        auth_header = request.headers.get('Authorization')
        user_id = User.validate_request(auth_header)
        if not user_id or isinstance(user_id, dict):
            return make_response(jsonify(location=Config.url+'/auth'), 401)

        if request.args.get('username'):
            user = User()
            return jsonify(username=user.get_username(user_id))

        study = Study()

        # Load specific study
        if request.args.get('id'):
            return jsonify(study=
                           study.get_study((request.args.get('id')), user_id))

        # Load all studies
        return jsonify(studies=study.get_studies(user_id))

    def post(self):
        # Check authentication
        auth_header = request.headers.get('Authorization')
        user_id = User.validate_request(auth_header)

        if not user_id or isinstance(user_id, dict):
            return make_response(jsonify(location=Config.url+'/auth'), 401)

        req = request.json
        study = Study()
        error = study.create_study(req['title'], req['description'], req['cards'], req['message'], user_id)
        date = datetime.datetime.now().isoformat()

        if error:
            return jsonify(error=error)

        # Create the response
        res = {
            'id': str(study.study_id),
            'title': req['title'],
            'abandonedNo': 0,
            'completedNo': 0,
            'editDate': date,
            'isLive': True,
            'launchedDate': date,
            'url': Config.url + '/study/' + str(study.study_id),
        }

        return jsonify(study=res)

    def delete(self):
        pass
