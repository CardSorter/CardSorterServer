from flask import current_app
from passlib.apps import custom_app_context as pwd_context

from ..db import get_db

class User:
    def __init__(self):
        with current_app.app_context():
            self.db = get_db()['users']
        self.password_hash = 0

    def create_user(self, username, password, email):
        if username:
            if self.db.find({'username': username}):
                return {'message': 'DUPLICATE USERNAME'}
        else:
            return {'message': 'EMPTY USERNAME'}

        if email:
            if self.db.find({'email': email}):
                return {'message': 'DUPLICATE EMAIL'}
        else:
            return {'message': 'EMPTY EMAIL'}

        if password:
            self._hash_password(password)
        else:
            return {'message': 'EMPTY PASSWORD'}

        self.db.insert_one({
            'username': username,
            'password': self.password_hash,
            'email': email
        })
        return None

    def _hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)