from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.models.base import db, generate_uuid, TimestampMixin

class Category(db.Model, TimestampMixin):
    """Product category taxonomy hierarchy."""
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    parent_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(180), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    # Relationships
    children = relationship("Category", backref=db.backref("parent", remote_side=[id]))
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name} ({self.slug})>"


class Product(db.Model, TimestampMixin):
    """Core product catalog model."""
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(280), unique=True, nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    brand = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    discount_price = Column(Numeric(12, 2), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=5)
    average_rating = Column(Numeric(3, 2), nullable=False, default=0.00)
    reviews_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_featured = Column(Boolean, nullable=False, default=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.display_order")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("ProductReview", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    inventory_transactions = relationship("InventoryTransaction", back_populates="product")

    @property
    def effective_price(self):
        """Return the lowest active price for the product."""
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price:
            return float(self.discount_price)
        return float(self.price)

    @property
    def primary_image(self):
        """Retrieve the primary display image URL if available."""
        for img in self.images:
            if img.is_primary:
                return img.image_url
        if self.images:
            return self.images[0].image_url
        return None

    def __repr__(self):
        return f"<Product {self.name} (SKU: {self.sku})>"


class ProductImage(db.Model):
    """Product gallery images."""
    __tablename__ = "product_images"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    alt_text = Column(String(255), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_primary = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    product = relationship("Product", back_populates="images")


class ProductAttribute(db.Model):
    """Key-value attributes (e.g. Color, Storage, Size)."""
    __tablename__ = "product_attributes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    attribute_name = Column(String(100), nullable=False)
    attribute_value = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    product = relationship("Product", back_populates="attributes")
