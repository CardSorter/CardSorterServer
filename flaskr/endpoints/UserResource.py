from flask import request, jsonify, make_response
from flask_restful import Resource

from ..entities.User import User
from flaskr.Config import Config


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
                'location': Config.url,
                'auth_token':  user.auth_token.decode()
            }))

        return resp
