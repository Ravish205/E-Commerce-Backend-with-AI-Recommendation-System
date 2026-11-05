import re
from typing import Dict, Any, List, Optional, Tuple
from backend.app.models.catalog import Product, Category
from backend.app.repositories.catalog_repo import CatalogRepository

def slugify(text: str) -> str:
    """Generate a clean URL slug from text."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")

class CatalogService:
    @staticmethod
    def serialize_product(product: Product, include_details: bool = False) -> Dict[str, Any]:
        data = {
            "id": product.id,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else None,
            "category_slug": product.category.slug if product.category else None,
            "name": product.name,
            "slug": product.slug,
            "sku": product.sku,
            "brand": product.brand,
            "short_description": product.short_description,
            "price": float(product.price),
            "discount_price": float(product.discount_price) if product.discount_price else None,
            "effective_price": product.effective_price,
            "stock": product.stock,
            "is_in_stock": product.stock > 0,
            "average_rating": float(product.average_rating),
            "reviews_count": product.reviews_count,
            "is_active": product.is_active,
            "is_featured": product.is_featured,
            "primary_image": product.primary_image,
            "created_at": product.created_at.isoformat() if product.created_at else None,
        }

        if include_details:
            data["description"] = product.description
            data["images"] = [
                {
                    "id": img.id,
                    "image_url": img.image_url,
                    "alt_text": img.alt_text,
                    "display_order": img.display_order,
                    "is_primary": img.is_primary,
                }
                for img in product.images
            ]
            data["attributes"] = [
                {
                    "id": attr.id,
                    "attribute_name": attr.attribute_name,
                    "attribute_value": attr.attribute_value,
                }
                for attr in product.attributes
            ]

        return data

    @staticmethod
    def serialize_category(category: Category) -> Dict[str, Any]:
        return {
            "id": category.id,
            "parent_id": category.parent_id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image_url": category.image_url,
            "is_active": category.is_active,
            "sort_order": category.sort_order,
        }

    @staticmethod
    def get_categories(active_only: bool = True) -> List[Dict[str, Any]]:
        categories = CatalogRepository.get_categories(active_only=active_only)
        return [CatalogService.serialize_category(c) for c in categories]

    @staticmethod
    def get_products(query_params: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        page = query_params.get("page", 1)
        limit = query_params.get("limit", 20)

        products, total = CatalogRepository.query_products(
            page=page,
            limit=limit,
            category_id=query_params.get("category_id"),
            category_slug=query_params.get("category_slug"),
            search=query_params.get("search"),
            brand=query_params.get("brand"),
            min_price=query_params.get("min_price"),
            max_price=query_params.get("max_price"),
            min_rating=query_params.get("min_rating"),
            sort_by=query_params.get("sort_by", "newest"),
            active_only=True,
        )

        total_pages = (total + limit - 1) // limit if total > 0 else 1

        meta = {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": total_pages,
        }

        return [CatalogService.serialize_product(p, include_details=False) for p in products], meta

    @staticmethod
    def get_product_detail(id_or_slug: str) -> Optional[Dict[str, Any]]:
        product = CatalogRepository.get_product_by_id(id_or_slug)
        if not product:
            product = CatalogRepository.get_product_by_slug(id_or_slug)
        if not product or not product.is_active:
            return None
        return CatalogService.serialize_product(product, include_details=True)

    @staticmethod
    def create_product(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        slug = slugify(data["name"])
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while CatalogRepository.get_product_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        data["slug"] = slug
        images_data = data.pop("images", [])
        attributes_data = data.pop("attributes", [])

        product = CatalogRepository.create_product(data, images_data, attributes_data)
        return True, "Product created successfully", CatalogService.serialize_product(product, include_details=True)

    @staticmethod
    def update_product(product_id: str, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        product = CatalogRepository.get_product_by_id(product_id)
        if not product:
            return False, "Product not found", None

        if "name" in data and data["name"] != product.name:
            data["slug"] = slugify(data["name"])

        updated = CatalogRepository.update_product(product, **data)
        return True, "Product updated successfully", CatalogService.serialize_product(updated, include_details=True)

    @staticmethod
    def delete_product(product_id: str) -> Tuple[bool, str]:
        product = CatalogRepository.get_product_by_id(product_id)
        if not product:
            return False, "Product not found"
        CatalogRepository.delete_product(product)
        return True, "Product deactivated successfully"
