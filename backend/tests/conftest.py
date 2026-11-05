import pytest
from backend.app import create_app
from backend.app.models.base import db
from backend.app.models.user import User
from backend.app.models.catalog import Category, Product, ProductImage
from backend.app.models.order import Coupon
from backend.app.utils.security import hash_password

@pytest.fixture(scope="function")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Seed test admin & test customer
        admin = User(
            email="admin.test@example.com",
            password_hash=hash_password("AdminPass123!"),
            first_name="Admin",
            last_name="Tester",
            role="admin",
            is_active=True,
            is_email_verified=True,
        )
        customer = User(
            email="customer.test@example.com",
            password_hash=hash_password("CustomerPass123!"),
            first_name="Customer",
            last_name="Tester",
            role="customer",
            is_active=True,
            is_email_verified=True,
        )
        cat = Category(
            name="Audio & Electronics",
            slug="audio-electronics",
            description="High quality test audio",
            is_active=True,
        )
        db.session.add_all([admin, customer, cat])
        db.session.flush()

        prod1 = Product(
            category_id=cat.id,
            name="Test Wireless ANC Headphones",
            slug="test-wireless-anc-headphones",
            sku="TST-ANC-01",
            brand="SoundCorp",
            description="Noise cancelling bluetooth over-ear headphones with 30 hour battery life and hi-fi audio.",
            price=15000.00,
            discount_price=12000.00,
            stock=10,
            is_active=True,
        )
        prod2 = Product(
            category_id=cat.id,
            name="Test Compact Studio Earbuds",
            slug="test-compact-studio-earbuds",
            sku="TST-EAR-02",
            brand="SoundCorp",
            description="True wireless compact earbuds with deep bass and high fidelity audio reproduction.",
            price=8000.00,
            discount_price=7000.00,
            stock=5,
            is_active=True,
        )
        prod_out_of_stock = Product(
            category_id=cat.id,
            name="Test Vintage Audio Player",
            slug="test-vintage-audio-player",
            sku="TST-VNT-03",
            brand="RetroAudio",
            description="Vintage cassette and vinyl audio player.",
            price=25000.00,
            stock=0,  # Out of stock
            is_active=True,
        )
        db.session.add_all([prod1, prod2, prod_out_of_stock])

        from datetime import datetime, timezone, timedelta
        coupon = Coupon(
            code="SAVE10",
            discount_type="percentage",
            discount_value=10.0,
            min_order_amount=1000.0,
            is_active=True,
            starts_at=datetime.now(timezone.utc) - timedelta(days=1),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        db.session.add(coupon)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def customer_token(client):
    res = client.post("/api/auth/login", json={
        "email": "customer.test@example.com",
        "password": "CustomerPass123!",
    })
    return res.get_json()["data"]["access_token"]

@pytest.fixture
def admin_token(client):
    res = client.post("/api/auth/login", json={
        "email": "admin.test@example.com",
        "password": "AdminPass123!",
    })
    return res.get_json()["data"]["access_token"]
