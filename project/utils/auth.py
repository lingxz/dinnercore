from project.config import BaseConfig
import jwt
from jwt import DecodeError, ExpiredSignature
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request


# Authentication and decorators
def create_token(user):
    payload = {
        # data
        'id': user.id,
        'username': user.username,
        # issued at
        'iat': datetime.utcnow(),
        # expiry
        'exp': datetime.utcnow() + timedelta(days=1)
    }

    token = jwt.encode(payload, BaseConfig.SECRET_KEY, algorithm='HS256')
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, BaseConfig.SECRET_KEY, algorithms='HS256')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        return f(*args, **kwargs)

    return decorated_function
