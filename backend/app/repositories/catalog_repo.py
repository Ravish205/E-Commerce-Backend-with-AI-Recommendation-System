from typing import Optional, List, Tuple
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import joinedload
from backend.app.models.base import db
from backend.app.models.catalog import Category, Product, ProductImage, ProductAttribute

class CatalogRepository:
    # --- Category Operations ---
    @staticmethod
    def get_categories(active_only: bool = True) -> List[Category]:
        query = Category.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Category.sort_order.asc(), Category.name.asc()).all()

    @staticmethod
    def get_category_by_id(category_id: str) -> Optional[Category]:
        return Category.query.filter_by(id=category_id).first()

    @staticmethod
    def get_category_by_slug(slug: str) -> Optional[Category]:
        return Category.query.filter_by(slug=slug).first()

    @staticmethod
    def create_category(name: str, slug: str, description: Optional[str] = None, image_url: Optional[str] = None, parent_id: Optional[str] = None, sort_order: int = 0) -> Category:
        category = Category(
            name=name,
            slug=slug,
            description=description,
            image_url=image_url,
            parent_id=parent_id,
            sort_order=sort_order,
            is_active=True,
        )
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def update_category(category: Category, **kwargs) -> Category:
        for k, v in kwargs.items():
            if hasattr(category, k) and v is not None:
                setattr(category, k, v)
        db.session.commit()
        return category

    @staticmethod
    def delete_category(category: Category) -> None:
        db.session.delete(category)
        db.session.commit()

    # --- Product Operations ---
    @staticmethod
    def get_product_by_id(product_id: str, active_only: bool = False) -> Optional[Product]:
        query = Product.query.options(
            joinedload(Product.images),
            joinedload(Product.attributes),
            joinedload(Product.category),
        ).filter(Product.id == product_id)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.first()

    @staticmethod
    def get_product_by_slug(slug: str, active_only: bool = False) -> Optional[Product]:
        query = Product.query.options(
            joinedload(Product.images),
            joinedload(Product.attributes),
            joinedload(Product.category),
        ).filter(Product.slug == slug)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.first()

    @staticmethod
    def query_products(
        page: int = 1,
        limit: int = 20,
        category_id: Optional[str] = None,
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "newest",
        active_only: bool = True,
    ) -> Tuple[List[Product], int]:
        query = Product.query.options(
            joinedload(Product.images),
            joinedload(Product.category),
        )

        if active_only:
            query = query.filter(Product.is_active == True)

        if category_id:
            query = query.filter(Product.category_id == category_id)
        elif category_slug:
            query = query.join(Product.category).filter(Category.slug == category_slug)

        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand.strip()}%"))

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.brand.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )

        if min_price is not None:
            query = query.filter(
                or_(
                    Product.discount_price >= min_price,
                    (Product.discount_price == None) & (Product.price >= min_price),
                )
            )

        if max_price is not None:
            query = query.filter(
                or_(
                    (Product.discount_price != None) & (Product.discount_price <= max_price),
                    (Product.discount_price == None) & (Product.price <= max_price),
                )
            )

        if min_rating is not None and min_rating > 0:
            query = query.filter(Product.average_rating >= min_rating)

        # Sorting
        if sort_by == "price_asc":
            query = query.order_by(asc(Product.price))
        elif sort_by == "price_desc":
            query = query.order_by(desc(Product.price))
        elif sort_by == "rating":
            query = query.order_by(desc(Product.average_rating), desc(Product.reviews_count))
        elif sort_by == "popularity":
            query = query.order_by(desc(Product.reviews_count), desc(Product.average_rating))
        else:  # 'newest'
            query = query.order_by(desc(Product.created_at))

        total = query.count()
        products = query.offset((page - 1) * limit).limit(limit).all()
        return products, total

    @staticmethod
    def create_product(product_data: dict, images_data: list = None, attributes_data: list = None) -> Product:
        product = Product(
            category_id=product_data["category_id"],
            name=product_data["name"].strip(),
            slug=product_data["slug"].strip(),
            sku=product_data["sku"].strip().upper(),
            brand=product_data["brand"].strip(),
            description=product_data["description"].strip(),
            short_description=product_data.get("short_description", "").strip() if product_data.get("short_description") else None,
            price=product_data["price"],
            discount_price=product_data.get("discount_price"),
            stock=product_data["stock"],
            low_stock_threshold=product_data.get("low_stock_threshold", 5),
            is_active=product_data.get("is_active", True),
            is_featured=product_data.get("is_featured", False),
        )
        db.session.add(product)
        db.session.flush()

        if images_data:
            for idx, img in enumerate(images_data):
                product_img = ProductImage(
                    product_id=product.id,
                    image_url=img["image_url"],
                    alt_text=img.get("alt_text", product.name),
                    display_order=img.get("display_order", idx),
                    is_primary=img.get("is_primary", idx == 0),
                )
                db.session.add(product_img)

        if attributes_data:
            for attr in attributes_data:
                product_attr = ProductAttribute(
                    product_id=product.id,
                    attribute_name=attr["attribute_name"].strip(),
                    attribute_value=attr["attribute_value"].strip(),
                )
                db.session.add(product_attr)

        db.session.commit()
        return product

    @staticmethod
    def update_product(product: Product, **kwargs) -> Product:
        for k, v in kwargs.items():
            if hasattr(product, k) and v is not None:
                setattr(product, k, v)
        db.session.commit()
        return product

    @staticmethod
    def delete_product(product: Product) -> None:
        # Soft delete: deactivating keeps order history intact
        product.is_active = False
        db.session.commit()
