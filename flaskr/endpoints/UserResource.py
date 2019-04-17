from flask import request, jsonify
from flask_restful import Resource

from ..entities.User import User


class UserResource(Resource):
    def get(self):
        pass

    def post(self):
        if request.args['register']:
            username = request.json.get('username')
            password = request.json.get('password')
            email = request.json.get('email')
            user = User()
            error_msg = user.create_user(username, password, email)

            if error_msg:
                return jsonify(error=error_msg)
            return jsonify(user={
                'username': username
            })


    def delete(self):
        pass
