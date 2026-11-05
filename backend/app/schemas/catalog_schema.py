from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    id = fields.String(dump_only=True)
    parent_id = fields.String(required=False, allow_none=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    slug = fields.String(required=False, validate=validate.Length(max=180))
    description = fields.String(required=False, allow_none=True)
    image_url = fields.String(required=False, allow_none=True)
    is_active = fields.Boolean(load_default=True)
    sort_order = fields.Integer(load_default=0)

class ProductAttributeSchema(Schema):
    attribute_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    attribute_value = fields.String(required=True, validate=validate.Length(min=1, max=255))

class ProductImageSchema(Schema):
    image_url = fields.String(required=True)
    alt_text = fields.String(required=False, allow_none=True)
    display_order = fields.Integer(load_default=0)
    is_primary = fields.Boolean(load_default=False)

class ProductCreateSchema(Schema):
    category_id = fields.String(required=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=255))
    sku = fields.String(required=True, validate=validate.Length(min=2, max=100))
    brand = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(required=True, validate=validate.Length(min=5))
    short_description = fields.String(required=False, allow_none=True)
    price = fields.Float(required=True, validate=validate.Range(min=0.01))
    discount_price = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0))
    stock = fields.Integer(required=True, validate=validate.Range(min=0))
    low_stock_threshold = fields.Integer(required=False, load_default=5, validate=validate.Range(min=0))
    is_active = fields.Boolean(required=False, load_default=True)
    is_featured = fields.Boolean(required=False, load_default=False)
    images = fields.List(fields.Nested(ProductImageSchema), required=False)
    attributes = fields.List(fields.Nested(ProductAttributeSchema), required=False)

class ProductUpdateSchema(Schema):
    category_id = fields.String(required=False)
    name = fields.String(required=False, validate=validate.Length(min=2, max=255))
    sku = fields.String(required=False, validate=validate.Length(min=2, max=100))
    brand = fields.String(required=False, validate=validate.Length(min=1, max=120))
    description = fields.String(required=False, validate=validate.Length(min=5))
    short_description = fields.String(required=False, allow_none=True)
    price = fields.Float(required=False, validate=validate.Range(min=0.01))
    discount_price = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0))
    stock = fields.Integer(required=False, validate=validate.Range(min=0))
    low_stock_threshold = fields.Integer(required=False, validate=validate.Range(min=0))
    is_active = fields.Boolean(required=False)
    is_featured = fields.Boolean(required=False)

class ProductQuerySchema(Schema):
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    limit = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))
    category_id = fields.String(required=False, allow_none=True)
    category_slug = fields.String(required=False, allow_none=True)
    search = fields.String(required=False, allow_none=True)
    brand = fields.String(required=False, allow_none=True)
    min_price = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0))
    max_price = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0))
    min_rating = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0, max=5))
    sort_by = fields.String(
        load_default="newest",
        validate=validate.OneOf(["newest", "price_asc", "price_desc", "rating", "popularity"])
    )
