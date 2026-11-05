from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=8, max=100))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone_number = fields.String(required=False, allow_none=True, validate=validate.Length(max=30))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class ProfileUpdateSchema(Schema):
    first_name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    phone_number = fields.String(required=False, allow_none=True, validate=validate.Length(max=30))

class ChangePasswordSchema(Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8, max=100))

class AddressSchema(Schema):
    address_type = fields.String(required=False, load_default="shipping", validate=validate.OneOf(["shipping", "billing"]))
    recipient_name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    phone = fields.String(required=True, validate=validate.Length(min=5, max=30))
    street_address = fields.String(required=True, validate=validate.Length(min=5, max=500))
    landmark = fields.String(required=False, allow_none=True, validate=validate.Length(max=255))
    city = fields.String(required=True, validate=validate.Length(min=2, max=100))
    state = fields.String(required=True, validate=validate.Length(min=2, max=100))
    postal_code = fields.String(required=True, validate=validate.Length(min=3, max=20))
    country = fields.String(required=False, load_default="India", validate=validate.Length(max=100))
    is_default = fields.Boolean(required=False, load_default=False)
