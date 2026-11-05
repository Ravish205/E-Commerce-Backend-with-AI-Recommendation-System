from marshmallow import Schema, fields, validate

class OrderCreateSchema(Schema):
    shipping_address_id = fields.String(required=False, allow_none=True)
    shipping_address = fields.Dict(required=False, allow_none=True)
    billing_address_id = fields.String(required=False, allow_none=True)
    billing_address = fields.Dict(required=False, allow_none=True)
    coupon_code = fields.String(required=False, allow_none=True)
    notes = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))

class OrderStatusUpdateSchema(Schema):
    status = fields.String(
        required=True,
        validate=validate.OneOf(["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"])
    )
    tracking_number = fields.String(required=False, allow_none=True)
    notes = fields.String(required=False, allow_none=True)

class PaymentVerifySchema(Schema):
    order_id = fields.String(required=True)
    gateway_order_id = fields.String(required=True)
    gateway_payment_id = fields.String(required=True)
    gateway_signature = fields.String(required=True)
