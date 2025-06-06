from flask import request, jsonify, make_response
from flask_restful import Resource
import datetime
from passlib.apps import custom_app_context as pwd_context

from ..entities.User import User
from flaskr.Config import Config
from bson import ObjectId
from flask import current_app

from ..db import get_db


class UserResource(Resource):
    def post(self):
        """
        Logins and registers the user.
        In register:
            The *request* body must contain the username, the password and the email.
            There are five *errors* that are returned:
                -DUPLICATE USERNAME
                -EMPTY USERNAME
                -DUPLICATE EMAIL
                -EMPTY EMAIL
                -EMPTY PASSWORD
            The *response* body will contain the fields:
                -location: the URL that the user will be redirected.
                -auth_token: the token used for authenticating the user's identity.
        In login:
            The *request* body must contain the username and the password.
            There are four *errors* that are returned:
                -USERNAME NOT FOUND
                -EMPTY USERNAME
                -INVALID PASSWORD
                -EMPTY PASSWORD
            The *response* body will contain the fields:
                -location: the URL that the user will be redirected.
                -auth_token: the token used for authenticating the user's identity.
        :return:
        """

        if len(request.args) > 0 and request.args['register']:
            username = request.json.get('username')
            password = request.json.get('password')
            email = request.json.get('email')
            user = User()
            error_msg = user.create_user(username, password, email)

            if error_msg:
                return jsonify(error=error_msg)

            resp = make_response(jsonify({
                'location': Config.url,
                'auth_token':  user.auth_token
            }))

        else:  # Login
            username = request.json.get('username')
            password = request.json.get('password')
            user = User()
            error_msg = user.verify_user(username, password)

            if error_msg:
                return jsonify(error=error_msg)

            resp = make_response(jsonify({
                'location': Config.url,
                'auth_token':  user.auth_token
            }))

        return resp
    def get(self):
         
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
         return make_response(jsonify(error="Missing Authorization header"), 401)
        
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        user_id = User.validate_request(token)

        if not user_id or isinstance(user_id, dict):
            return make_response(jsonify(location=Config.url+'auth/'), 401)
        
        with current_app.app_context():
           db = get_db()['users']
           user_doc = db.find_one({'_id': ObjectId(user_id)}, {'username': 1, 'email': 1})
           
        
        if not user_doc:
            return jsonify(error="User not found"), 404
        
       

        return jsonify(username=user_doc['username'], email=user_doc['email'])
    

    def put(self):
        
       auth_header = request.headers.get('Authorization')
       token = auth_header.split(" ")[1] if " " in auth_header else auth_header
       user_id = User.validate_request(token)
       if not user_id or isinstance(user_id, dict):
         return make_response(jsonify(location=Config.url + 'auth/'), 401)
 
    
       req = request.json
       updated_properties = {}

       if 'newUsername' in req and req['newUsername'].strip():
         updated_properties['username'] = req['newUsername']

       if 'newEmail' in req and req['newEmail'].strip():
         updated_properties['email'] = req['newEmail']

       if 'newPassword' in req and req['newPassword'].strip():
         updated_properties['password'] = User._hash_password(req['newPassword'])

       edit_date = datetime.datetime.now().isoformat()

       if updated_properties:
         with current_app.app_context():
            db = get_db()['users']
            result = db.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': updated_properties}
            )
            if result.modified_count > 0:
                return '', 200
            else:
                return '', 204  
       else:
         return '', 400  

