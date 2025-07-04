import datetime
from functools import wraps
from errors.exceptions import APIError, AuthError
import jwt
from flask import request, jsonify, g, Blueprint, current_app
from sqlalchemy.exc import SQLAlchemyError
from models import User
auth = Blueprint('auth', __name__)

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json(silent=True)
        if not data:
            raise APIError("No data provided", status_code=400)
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise APIError("Email and password are required", status_code=400)
        try:
            s = g.db
            user = s.query(User).filter_by(email=email).first()
            if user and user.check_password(password):
                g.user_id = user.id
                return func(*args, **kwargs)
            else:
                raise AuthError("Wrong password or email")
        except SQLAlchemyError as e:
            raise APIError("Database error", status_code=500)

    return wrapper

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Please provide email and password'}), 400
    s = g.db
    exists = s.query(User).filter_by(email=email).first()
    if exists:
        return jsonify({'message': 'Email already registered'}), 400
    user = User(email=email)
    user.set_password(password)
    s.add(user)
    return jsonify({'message': 'User registered'}), 201

@auth.route('/get_token', methods=['POST'])
@authenticate
def get_token():
    payload ={
        'user_id': g.user_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})

@auth.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_id = int(data.get('user_id'))
    s = g.db
    user = s.query(User).filter_by(id=user_id).first()
    s.delete(user)
    return jsonify({'message': 'User deleted'}), 201
