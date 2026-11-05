from flask import Blueprint, request
from marshmallow import ValidationError
from backend.app.schemas.catalog_schema import ProductQuerySchema
from backend.app.services.catalog_service import CatalogService
from backend.app.repositories.catalog_repo import CatalogRepository
from backend.app.utils.response import api_response

catalog_bp = Blueprint("catalog", __name__, url_prefix="/api")

query_schema = ProductQuerySchema()

@catalog_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = CatalogService.get_categories(active_only=True)
    return api_response(success=True, message="Categories retrieved", data=categories, status_code=200)


@catalog_bp.route("/categories/<string:slug>", methods=["GET"])
def get_category_by_slug(slug: str):
    category = CatalogRepository.get_category_by_slug(slug)
    if not category or not category.is_active:
        return api_response(success=False, message="Category not found", status_code=404)
    return api_response(
        success=True,
        message="Category details retrieved",
        data=CatalogService.serialize_category(category),
        status_code=200,
    )


@catalog_bp.route("/products", methods=["GET"])
def get_products():
    try:
        query_params = query_schema.load(request.args.to_dict())
    except ValidationError as err:
        return api_response(success=False, message="Invalid query parameters", errors=err.messages, status_code=400)

    products, meta = CatalogService.get_products(query_params)
    return api_response(
        success=True,
        message="Products retrieved",
        data=products,
        meta=meta,
        status_code=200,
    )


@catalog_bp.route("/products/<string:id_or_slug>", methods=["GET"])
def get_product(id_or_slug: str):
    product = CatalogService.get_product_detail(id_or_slug)
    if not product:
        return api_response(success=False, message="Product not found", status_code=404)
    return api_response(success=True, message="Product details retrieved", data=product, status_code=200)
