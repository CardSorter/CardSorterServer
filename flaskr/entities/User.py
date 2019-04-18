import datetime
import jwt
from flask import current_app
from passlib.apps import custom_app_context as pwd_context

from ..db import get_db


class User:
    def __init__(self):
        with current_app.app_context():
            self.db = get_db()['users']
        self.password_hash = 0
        self.auth_token = 0

    def create_user(self, username, password, email):
        if username:
            if len(list(self.db.find({'username': username}))) > 0:
                return {'message': 'DUPLICATE USERNAME'}
        else:
            return {'message': 'EMPTY USERNAME'}

        if email:
            if len(list(self.db.find({'email': email}))) > 0:
                return {'message': 'DUPLICATE EMAIL'}
        else:
            return {'message': 'EMPTY EMAIL'}

        if password:
            self._hash_password(password)
        else:
            return {'message': 'EMPTY PASSWORD'}

        user = self.db.insert_one({
            'username': username,
            'password': self.password_hash,
            'email': email
        })

        self.auth_token = User._encode_auth_token(str(user.inserted_id))
        return None

    def verify_user(self, username, password):
        if username:
            if len(list(self.db.find({'username': username}))) == 0:
                return {'message': 'USERNAME NOT FOUND'}
        else:
            return {'message': 'EMPTY USERNAME'}

        if password:
            user = list(self.db.find({'username': username}, {'password': 1}))[0]
            self.password_hash = user['password']
            if self._verify_password(password):
                self.auth_token = User._encode_auth_token(str(user['_id']))
            else:
                return {'message': 'INVALID PASSWORD'}

        else:
            return {'message': 'EMPTY PASSWORD'}

    @staticmethod
    def validate_request(auth_header):
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            return User._decode_auth_token(auth_token)
        else:
            return False


    def _hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def _verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    @staticmethod
    def _encode_auth_token(user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def _decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return {'message': 'SIGNATURE EXPIRED'}
        except jwt.InvalidTokenError:
            return {'message': 'INVALID TOKEN'}