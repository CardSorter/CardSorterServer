import datetime
import jwt
from flask import current_app
from passlib.apps import custom_app_context as pwd_context
from ..db import conn

class User:
    def __init__(self):
        self.password_hash = 0
        self.auth_token = 0
        with current_app.app_context():
            self.cur = conn.cursor()

    def create_user(self, username, password, email):

        if username:
            self.cur.execute("""SELECT USERNAME FROM USER_TABLE WHERE USERNAME = %s;""", (username,))
            if self.cur.fetchall():
                return {'message': 'DUPLICATE USERNAME'}
        else:
            return {'message': 'EMPTY USERNAME'}

        if email:
            self.cur.execute("""SELECT EMAIL FROM USER_TABLE WHERE EMAIL = %s;""", (email,))
            if self.cur.fetchall():
                return {'message': 'DUPLICATE EMAIL'}
        else:
            return {'message': 'EMPTY EMAIL'}

        if password:
            self._hash_password(password)
        else:
            return {'message': 'EMPTY PASSWORD'}

        self.cur.execute("INSERT INTO USER_TABLE (USERNAME, PASS, EMAIL) "
                         "VALUES (%s, %s, %s) RETURNING id;",
                         (username, self.password_hash, email,))
        conn.commit()

        user = self.cur.fetchone()[0]
        self.auth_token = User._encode_auth_token(str(user))
        return None

    def verify_user(self, username, password):
        if username:
            self.cur.execute("""SELECT USERNAME FROM USER_TABLE WHERE USERNAME = %s;""", (username,))
            if not self.cur.fetchall():
                return {'message': 'USERNAME NOT FOUND'}
        else:
            return {'message': 'EMPTY USERNAME'}

        if password:
            self.cur.execute("""SELECT ID, PASS FROM USER_TABLE WHERE USERNAME = %s;""", (username,))
            _id, _pass = self.cur.fetchone()
            self.password_hash = str(_pass)
            if self._verify_password(password):
                self.auth_token = User._encode_auth_token(str(_id))
            else:
                return {'message': 'INVALID PASSWORD'}
        else:
            return {'message': 'EMPTY PASSWORD'}

    def get_username(self, user_id):
        self.cur.execute("""SELECT USERNAME FROM USER_TABLE WHERE ID = %s""", (user_id,))
        return self.cur.fetchone()[0].strip()

    @staticmethod
    def validate_request(auth_token):
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
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=60),
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
        :return: obj|string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return {'message': 'SIGNATURE EXPIRED'}
        except jwt.InvalidTokenError:
            return {'message': 'INVALID TOKEN'}