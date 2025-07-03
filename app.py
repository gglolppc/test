from flask import Flask, request, jsonify, g
from sqlalchemy.exc import SQLAlchemyError
from models import User, Note
from database import Base, engine, Session
from sqlalchemy import event
import datetime
import jwt
from functools import wraps

app = Flask(__name__)
app.secret_key = 'keykey'
Base.metadata.create_all(engine)

@app.before_request
def before_request():
    g.db = Session()
@app.teardown_request
def close_session(exception=None):
    db = getattr(g, 'db', None)
    if db is not None:
        if exception:
            db.rollback()
        else:
            db.commit()
        db.close()
@event.listens_for(engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'message': 'Please provide email and password'}), 400
        try:
            s = g.db
            user = s.query(User).filter_by(email=email).first()
            if user and user.check_password(password):
                g.user_id = user.id
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        except SQLAlchemyError as e:
            return jsonify({'message': 'Database error', 'details': str(e)}), 500
        except AttributeError as e:
            return jsonify({'message': 'Internal error', 'details': str(e)}), 500
        except Exception as e:
            return jsonify({'message': 'Unexpected error', 'details': str(e)}), 500
    return wrapper
def check_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'message': 'No token provided'}), 400
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Signature expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return func(*args, **kwargs)
    return wrapper


@app.route('/register', methods=['POST'])
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

@app.route('/get_token', methods=['POST'])
@authenticate
def get_token():
    payload ={
        'user_id': g.user_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})

@app.route('/add_note', methods=['POST'])
@check_token
def add_note():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    title = data.get('title')
    content = data.get('content')
    if not title:
        return jsonify({'message': 'Please provide title'}), 400
    try:
        s = g.db
        note = Note(title=title, content=content, user_id=g.user_id)
        s.add(note)
        return jsonify({'message': 'Note added'}), 201
    except SQLAlchemyError as e:
        return jsonify({'message': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'message': 'Unexpected error', 'details': str(e)}), 500

@app.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_id = int(data.get('user_id'))
    s = g.db
    user = s.query(User).filter_by(id=user_id).first()
    s.delete(user)
    return jsonify({'message': 'User deleted'}), 201




if __name__ == '__main__':
    app.run()