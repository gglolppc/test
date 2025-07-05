from functools import wraps

from flask import request
from marshmallow import Schema, fields, ValidationError

from errors.exceptions import APIError


class NoteSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Raw(required=False)

schema = NoteSchema()

def validate_json(f):
    @wraps
    def validate(*args, **kwargs):
        data = schema.load(request.json)
        return f(data, *args, **kwargs)
    return validate
