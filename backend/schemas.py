from marshmallow import Schema, fields, validate

class PatientSchema(Schema):
    id = fields.Int(dump_only=True)  # ID should only be read, not set manually
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    age = fields.Int(required=True, validate=validate.Range(min=0, max=120))
