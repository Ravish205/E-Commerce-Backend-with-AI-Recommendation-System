from marshmallow import Schema, fields, validate

class InteractionTrackSchema(Schema):
    product_id = fields.String(required=True)
    interaction_type = fields.String(
        required=True,
        validate=validate.OneOf(["view", "search_click", "wishlist_add", "cart_add", "purchase", "review"])
    )
    session_id = fields.String(required=False, allow_none=True)
    dwell_time_seconds = fields.Integer(required=False, load_default=0, validate=validate.Range(min=0))
    event_metadata = fields.Dict(required=False, allow_none=True)
