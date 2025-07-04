from functools import wraps
import jwt
from flask import jsonify, request, g, current_app
from errors.exceptions import APIError, AuthError

def check_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            raise AuthError("Please provide a token")
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            raise AuthError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthError("Invalid token")
        return func(*args, **kwargs)
    return wrapper