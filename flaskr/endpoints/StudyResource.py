from flask import request, jsonify, make_response
from flask_restful import Resource
import datetime

from flaskr.Config import Config
from flaskr.entities.Study import Study
from flaskr.entities.User import User


class StudyResource(Resource):
    def get(self):
        """
        Checks the authentication, returns the user details, returns all the studies, returns a specific study with full
        details based on the id, returns the clusters of a study.
        In *all cases*:
            The authentication headers are used to identify the user.
            If the authentication is unsuccessful the redirect location is returned.
        In *get username*:
            The parameter username is passed.
            The username is returned.
        In *get specific study*:
            The id is passed as a parameter.
            The study object is returned.
        In *get cluster of study*:
            The id is passed as a parameter.
            The cluster parameter is set to true.
            The cluster is returned.
        In *get all studies*:
            This is the default behaviour.
            The studies that belong to the user are returned.
            The studies don't include all information.
        """

        # Check authentication
        auth_header = request.headers.get('Authorization')
        user_id = User.validate_request(auth_header)
        if not user_id or isinstance(user_id, dict):
            return make_response(jsonify(location=Config.url+'auth/'), 401)

        if request.args.get('username'):
            user = User()
            return jsonify(username=user.get_username(user_id))

        study = Study()

        # Load specific study
        if request.args.get('id'):
            # Load the clusters of a study
            if request.args.get('clusters'):
                return jsonify(clusters=
                               study.get_clusters((request.args.get('id')), user_id))
            return jsonify(study=
                           study.get_study((request.args.get('id')), user_id))

        # Load all studies
        return jsonify(studies=study.get_studies(user_id))

    def post(self):
        """
        Creates a new study.
        Default case:
            The authentication headers are used to identify the user.
            If the authentication is unsuccessful the redirect location is returned.
            The study creation object is passed in the body of the request as a JSON.
            The created resource (study) is returned.
        """

        # Check authentication
        auth_header = request.headers.get('Authorization')
        user_id = User.validate_request(auth_header)

        if not user_id or isinstance(user_id, dict):
            return make_response(jsonify(location=Config.url+'auth/'), 401)
        
        req = request.json
        study = Study()
        if 'link' in req:
            error = study.create_study(req['title'], req['description'], req['cards'], req['message'], req['link'],user_id)
        else:
            error = study.create_study(req['title'], req['description'], req['cards'], req['message'], 'undefined',user_id)
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
            'url_to_study': Config.url + 'study/' + str(study.study_id),
            'share_url': Config.url + 'sort/' + '?id=' + str(study.study_id),
        }

        return jsonify(study=res)
    
    def put(self):
        """
        Edits a study by changing the title or isLive status.
        Request body should contain JSON with 'id', 'title', and/or 'isLive'.
        """
        # Check authentication
        auth_header = request.headers.get('Authorization')
        user_id = User.validate_request(auth_header)
        if not user_id or isinstance(user_id, dict):
            return make_response(jsonify(location=Config.url+'auth/'), 401)
              
        
        study_id = request.args.get('id')  # Get the study ID from the request
        study = Study()
        
        req = request.json
        updated_properties = {}
        if 'title' in req:
            updated_properties['title'] = req['title']

        if 'isLive' in req:
            updated_properties['is_live'] = req['isLive']
        
        if req['isLive'] == False:
            updated_properties['endDate'] = datetime.datetime.now().isoformat();
        if 'description' in req:
            updated_properties['description'] = req['description']
       
        editDate = datetime.datetime.now().isoformat();
        if updated_properties:
            if study.update_study(study_id,editDate, **updated_properties):
                return '',200    
        else:
            return '', 400
        
    def delete(self):
        """
        Deletes a study based on the provided study ID.
        The study ID is passed as a parameter in the request.
        """
        # Check authentication
        auth_header = request.headers.get('Authorization')
        user_id = User.validate_request(auth_header)
        if not user_id or isinstance(user_id, dict):
            return make_response(jsonify(location=Config.url+'auth/'), 401)
        
        study_id = request.args.get('id')  # Get the study ID from the request
        study = Study()

        if study.delete_study(study_id):
            return '', 204  # Successfully deleted
        else:
            return '', 500  # Internal server error during deletion

