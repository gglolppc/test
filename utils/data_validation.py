from marshmallow import Schema, fields, ValidationError

class NoteSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Raw(required=False)

schema = NoteSchema()

