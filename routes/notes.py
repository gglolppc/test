from flask import request, jsonify, g, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from errors.exceptions import APIError
from models import Note
from utils.check_token import check_token
from utils.data_validation import schema

notes = Blueprint('notes', __name__)


@notes.route('/add_note', methods=['POST'])
@check_token
def add_note():
    try:
        data = request.get_json(silent=True)
        if not data:
            raise APIError(message="Missing data", status_code=400)
        data = schema.load(request.json)
        title = data.get('title')
        content = data.get('content')
        s = g.db
        note = Note(user_id = g.user_id, title=title, content=content)
        s.add(note)

        return jsonify({'message': 'Note added with success',
                        'title': title,
                        'content': content
                        })
    except SQLAlchemyError:
        raise APIError('Database error')
    except ValidationError as err:
        raise APIError(f"Validation error: {err.messages}", status_code=400)


@notes.route('/get_notes', methods=['GET'])
@check_token
def get_notes():
    s = g.db
    user_notes = s.query(Note).filter_by(user_id=g.user_id).all()
    if not user_notes:
        return jsonify({'message': 'No notes found'}), 200
    result = [note.to_dict() for note in user_notes]

    return jsonify(result), 200

@notes.route('/<int:note_id>', methods=['DELETE'])
@check_token
def delete_note(note_id):
    if request.data:
        raise APIError('DELETE request should not have body')
    s = g.db
    note = s.query(Note).filter_by(user_id=g.user_id, id = note_id).first()
    if not note:
        raise APIError('Note not found', status_code=404)
    s.delete(note)
    return jsonify({'message': 'Note deleted'}), 200

@notes.route('/<int:note_id>', methods=['PUT'])
@check_token
def update_note(note_id):
    data = request.get_json()
    if not data:
        raise APIError('No data provided')
    title = data.get('title')
    content = data.get('content')
    if not title:
        raise APIError('Please provide title')
    try:
        s = g.db
        note = s.query(Note).filter_by(user_id=g.user_id, id = note_id).first()
        if not note:
            raise APIError('Note not found or access denied', status_code=404, error_type='NotFound')
        note.title = title
        if content:
            note.content = content
        return jsonify({'message': 'Note updated'}), 200
    except APIError:
        raise
    except SQLAlchemyError:
        raise APIError('Database error', status_code=500, error_type='DatabaseError')
    except Exception as e:
        raise APIError('Unexpected error', status_code=500, error_type='APIError')



