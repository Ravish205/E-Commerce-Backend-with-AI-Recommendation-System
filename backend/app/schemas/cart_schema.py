from marshmallow import Schema, fields, validate

class CartItemAddSchema(Schema):
    product_id = fields.String(required=True)
    quantity = fields.Integer(required=False, load_default=1, validate=validate.Range(min=1, max=50))

class CartItemUpdateSchema(Schema):
    quantity = fields.Integer(required=True, validate=validate.Range(min=1, max=50))

class ApplyCouponSchema(Schema):
    code = fields.String(required=True, validate=validate.Length(min=2, max=50))
