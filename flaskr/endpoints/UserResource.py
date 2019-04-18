import base64

from flask import request, jsonify, make_response, url_for, after_this_request
from flask_restful import Resource

from ..entities.User import User


class UserResource(Resource):
    def get(self):
        pass

    def post(self):

        if len(request.args) > 0 and request.args['register']:
            username = request.json.get('username')
            password = request.json.get('password')
            email = request.json.get('email')
            user = User()
            error_msg = user.create_user(username, password, email)

            if error_msg:
                return jsonify(error=error_msg)

            resp = make_response(jsonify({
                'location': url_for('designer.show'),
                'auth_token':  user.auth_token.decode()
            }))

        else:  # Login
            username = request.json.get('username')
            password = request.json.get('password')
            user = User()
            error_msg = user.verify_user(username, password)

            if error_msg:
                return jsonify(error=error_msg)

            resp = make_response(jsonify({
                'location': url_for('designer.show'),
                'auth_token':  user.auth_token.decode()
            }))

        return resp

    def delete(self):
        pass
