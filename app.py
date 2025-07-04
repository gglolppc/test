from flask import Flask, g, abort, jsonify
from dotenv import load_dotenv
import os
from database import Base, engine, Session
from sqlalchemy import event

from errors.exceptions import APIError
from errors.handlers import register_error_handlers
from routes.auth import auth
from routes.notes import notes
load_dotenv()

app = Flask(__name__)
register_error_handlers(app)
app.secret_key = os.getenv('SECRET_KEY')

Base.metadata.create_all(engine)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(notes, url_prefix='/notes')

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

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response







if __name__ == '__main__':
    app.run()