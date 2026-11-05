from marshmallow import Schema, fields, validate

class ReviewCreateSchema(Schema):
    product_id = fields.String(required=True)
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    title = fields.String(required=True, validate=validate.Length(min=2, max=200))
    comment = fields.String(required=True, validate=validate.Length(min=5, max=3000))

class ReviewModerateSchema(Schema):
    is_approved = fields.Boolean(required=True)
