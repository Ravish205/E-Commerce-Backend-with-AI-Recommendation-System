import os
from datetime import datetime, timezone, timedelta
from backend.app import create_app
from backend.app.models.base import db
from backend.app.models.user import User, UserAddress
from backend.app.models.catalog import Category, Product, ProductImage, ProductAttribute
from backend.app.models.order import Order, OrderItem, Coupon, InventoryTransaction
from backend.app.models.review import ProductReview
from backend.app.models.recommendation import UserInteraction
from backend.app.repositories.order_repo import OrderRepository
from backend.app.utils.security import hash_password

def seed_database():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        print("Cleaning and initializing database tables...")
        db.create_all()

        # Check if already seeded
        if User.query.filter_by(email="admin@ecommerce.com").first():
            print("Database is already seeded.")
            return

        print("Seeding Users...")
        admin = User(
            email="admin@ecommerce.com",
            password_hash=hash_password("AdminPass123!"),
            first_name="Store",
            last_name="Administrator",
            role="admin",
            is_active=True,
            is_email_verified=True,
            phone_number="+91 9876543210",
        )
        customer1 = User(
            email="rahul.sharma@example.com",
            password_hash=hash_password("CustomerPass123!"),
            first_name="Rahul",
            last_name="Sharma",
            role="customer",
            is_active=True,
            is_email_verified=True,
            phone_number="+91 9812345678",
        )
        customer2 = User(
            email="priya.patel@example.com",
            password_hash=hash_password("CustomerPass123!"),
            first_name="Priya",
            last_name="Patel",
            role="customer",
            is_active=True,
            is_email_verified=True,
            phone_number="+91 9823456789",
        )
        db.session.add_all([admin, customer1, customer2])
        db.session.flush()

        # Add Addresses for customer1
        addr1 = UserAddress(
            user_id=customer1.id,
            address_type="shipping",
            recipient_name="Rahul Sharma",
            phone="+91 9812345678",
            street_address="Flat 402, Green Glen Layout, Bellandur",
            landmark="Near EcoSpace",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560103",
            country="India",
            is_default=True,
        )
        db.session.add(addr1)

        print("Seeding Categories...")
        categories = [
            Category(name="Audio & Headphones", slug="audio-headphones", description="High-fidelity wireless headphones, earbuds, and premium sound systems.", sort_order=1),
            Category(name="Laptops & Computing", slug="laptops-computing", description="Ultra-portable laptops, workstation notebooks, and desktop peripherals.", sort_order=2),
            Category(name="Smartphones & Tablets", slug="smartphones-tablets", description="Flagship mobile phones, 5G smartphones, and tablet computers.", sort_order=3),
            Category(name="Smart Home & Wearables", slug="smart-home-wearables", description="Fitness smartwatches, ambient smart lighting, and connected home tech.", sort_order=4),
            Category(name="Photography & Video", slug="photography-video", description="Mirrorless cameras, premium lenses, gimbals, and creator accessories.", sort_order=5),
        ]
        db.session.add_all(categories)
        db.session.flush()

        cat_map = {c.slug: c.id for c in categories}

        print("Seeding Products...")
        products_data = [
            # Audio
            {
                "category_id": cat_map["audio-headphones"],
                "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
                "slug": "sony-wh-1000xm5-wireless-noise-cancelling-headphones",
                "sku": "SNY-WH1000XM5-BLK",
                "brand": "Sony",
                "description": "Industry-leading noise cancellation optimized with two processors and eight microphones. Exceptional sound quality engineered with the integrated Processor V1, supporting High-Resolution Audio Wireless via LDAC.",
                "short_description": "Industry-leading noise cancelling wireless headphones with 30-hour battery life.",
                "price": 29990.00,
                "discount_price": 26990.00,
                "stock": 25,
                "average_rating": 4.80,
                "reviews_count": 14,
                "is_featured": True,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80", "is_primary": True},
                    {"image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80", "is_primary": False},
                ],
                "attributes": [
                    {"attribute_name": "Battery Life", "attribute_value": "30 Hours"},
                    {"attribute_name": "Connectivity", "attribute_value": "Bluetooth 5.2 / LDAC"},
                    {"attribute_name": "Color", "attribute_value": "Midnight Black"},
                ],
            },
            {
                "category_id": cat_map["audio-headphones"],
                "name": "Bose QuietComfort Ultra Wireless Headphones",
                "slug": "bose-quietcomfort-ultra-wireless-headphones",
                "sku": "BSE-QCULTRA-WHT",
                "brand": "Bose",
                "description": "Spatialized audio breakthrough for immersive listening that makes music feel more real than ever. CustomTune technology personalizes the noise cancellation and sound performance to your ear shape.",
                "short_description": "World-class active noise cancellation with breakthrough Bose Immersive Audio.",
                "price": 35900.00,
                "discount_price": 32900.00,
                "stock": 18,
                "average_rating": 4.70,
                "reviews_count": 9,
                "is_featured": False,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Battery Life", "attribute_value": "24 Hours"},
                    {"attribute_name": "Color", "attribute_value": "White Smoke"},
                ],
            },
            {
                "category_id": cat_map["audio-headphones"],
                "name": "Apple AirPods Pro (2nd Generation, USB-C)",
                "slug": "apple-airpods-pro-2nd-gen-usb-c",
                "sku": "APL-AIRPODSPRO-2",
                "brand": "Apple",
                "description": "Powered by the Apple H2 chip with next-level Active Noise Cancellation and Adaptive Audio. Personalized Spatial Audio with dynamic head tracking places sound all around you.",
                "short_description": "Active Noise Cancellation, Adaptive Audio, and MagSafe Charging Case (USB-C).",
                "price": 24900.00,
                "discount_price": 22990.00,
                "stock": 40,
                "average_rating": 4.90,
                "reviews_count": 28,
                "is_featured": True,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Chip", "attribute_value": "Apple H2"},
                    {"attribute_name": "Charging Case", "attribute_value": "USB-C MagSafe"},
                ],
            },
            # Laptops
            {
                "category_id": cat_map["laptops-computing"],
                "name": "Apple MacBook Pro 14-inch (M3 Pro Chip, 18GB RAM, 512GB SSD)",
                "slug": "apple-macbook-pro-14-m3-pro",
                "sku": "APL-MBP14-M3PRO",
                "brand": "Apple",
                "description": "Liquid Retina XDR display with ProMotion 120Hz refresh rate. Powered by M3 Pro with 11-core CPU and 14-core GPU. Up to 18 hours of battery life with unified memory architecture.",
                "short_description": "14.2-inch Liquid Retina XDR display, M3 Pro chip, 18GB Unified Memory.",
                "price": 199900.00,
                "discount_price": 184900.00,
                "stock": 12,
                "average_rating": 4.90,
                "reviews_count": 16,
                "is_featured": True,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Processor", "attribute_value": "Apple M3 Pro"},
                    {"attribute_name": "RAM", "attribute_value": "18GB Unified"},
                    {"attribute_name": "Storage", "attribute_value": "512GB SSD"},
                ],
            },
            {
                "category_id": cat_map["laptops-computing"],
                "name": "Dell XPS 15 9530 Laptop (Intel Core i7-13700H, 16GB, 1TB SSD, RTX 4050)",
                "slug": "dell-xps-15-9530-intel-core-i7",
                "sku": "DEL-XPS15-9530",
                "brand": "Dell",
                "description": "Precision-crafted 15.6-inch OLED InfinityEdge display with vibrant color reproduction. High-performance computing powered by 13th Gen Intel Core i7 and dedicated NVIDIA GeForce RTX graphics.",
                "short_description": "15.6-inch 3.5K OLED InfinityEdge, Core i7-13700H, RTX 4050 graphics.",
                "price": 174990.00,
                "discount_price": 162990.00,
                "stock": 8,
                "average_rating": 4.60,
                "reviews_count": 7,
                "is_featured": False,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Processor", "attribute_value": "Intel Core i7-13700H"},
                    {"attribute_name": "GPU", "attribute_value": "NVIDIA RTX 4050 6GB"},
                    {"attribute_name": "Display", "attribute_value": "15.6-inch 3.5K OLED"},
                ],
            },
            # Smartphones
            {
                "category_id": cat_map["smartphones-tablets"],
                "name": "Apple iPhone 15 Pro (128GB, Natural Titanium)",
                "slug": "apple-iphone-15-pro-128gb-natural-titanium",
                "sku": "APL-IPH15P-128-NAT",
                "brand": "Apple",
                "description": "Forged in aerospace-grade titanium with textured matte glass back. Super Retina XDR display with ProMotion up to 120Hz. A17 Pro chip with 6-core GPU, customizable Action button, and 48MP main camera.",
                "short_description": "6.1-inch Super Retina XDR, A17 Pro chip, Titanium design with Action button.",
                "price": 134900.00,
                "discount_price": 127900.00,
                "stock": 30,
                "average_rating": 4.85,
                "reviews_count": 35,
                "is_featured": True,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Storage", "attribute_value": "128GB"},
                    {"attribute_name": "Chip", "attribute_value": "A17 Pro"},
                    {"attribute_name": "Material", "attribute_value": "Titanium"},
                ],
            },
            {
                "category_id": cat_map["smartphones-tablets"],
                "name": "Samsung Galaxy S24 Ultra (256GB, Titanium Gray)",
                "slug": "samsung-galaxy-s24-ultra-256gb",
                "sku": "SAM-S24U-256-GRY",
                "brand": "Samsung",
                "description": "6.8-inch Dynamic AMOLED 2X display with Corning Gorilla Armor anti-reflective glass. Snapdragon 8 Gen 3 for Galaxy, built-in S Pen, and 200MP quad-telephoto camera with Galaxy AI assistance.",
                "short_description": "6.8-inch 120Hz AMOLED, Snapdragon 8 Gen 3, 200MP Camera with Galaxy AI.",
                "price": 129999.00,
                "discount_price": 119999.00,
                "stock": 20,
                "average_rating": 4.80,
                "reviews_count": 22,
                "is_featured": True,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "RAM", "attribute_value": "12GB"},
                    {"attribute_name": "Main Camera", "attribute_value": "200MP Optical"},
                    {"attribute_name": "Stylus", "attribute_value": "Embedded S Pen"},
                ],
            },
            # Smart Home & Wearables
            {
                "category_id": cat_map["smart-home-wearables"],
                "name": "Apple Watch Series 9 GPS 45mm Midnight Aluminum",
                "slug": "apple-watch-series-9-gps-45mm-midnight",
                "sku": "APL-WATCH-S9-45",
                "brand": "Apple",
                "description": "Powered by the S9 SiP enabling a super-bright Always-On display and magical Double Tap gesture. Advanced health sensors for blood oxygen, ECG, sleep tracking, and temperature sensing.",
                "short_description": "45mm Midnight Aluminum case with Sport Band, S9 SiP, and Double Tap gesture.",
                "price": 44900.00,
                "discount_price": 41900.00,
                "stock": 15,
                "average_rating": 4.75,
                "reviews_count": 19,
                "is_featured": False,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Case Size", "attribute_value": "45mm"},
                    {"attribute_name": "Water Resistance", "attribute_value": "50m (Swimproof)"},
                ],
            },
            # Photography
            {
                "category_id": cat_map["photography-video"],
                "name": "Sony Alpha A7 IV Full-Frame Mirrorless Camera Body",
                "slug": "sony-alpha-a7-iv-full-frame-camera-body",
                "sku": "SNY-ILCE7M4-BODY",
                "brand": "Sony",
                "description": "33MP full-frame Exmor R back-illuminated CMOS sensor with BIONZ XR processing engine. 4K 60p recording, 10-bit 4:2:2 color depth, and real-time Eye AF for humans, animals, and birds.",
                "short_description": "33MP Full-Frame Exmor R sensor, 4K 60p 10-bit 4:2:2 video, real-time Eye AF.",
                "price": 224990.00,
                "discount_price": 209990.00,
                "stock": 6,
                "average_rating": 4.90,
                "reviews_count": 11,
                "is_featured": True,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Sensor", "attribute_value": "33MP Full-Frame CMOS"},
                    {"attribute_name": "Video", "attribute_value": "4K 60p 10-Bit"},
                ],
            },
            {
                "category_id": cat_map["photography-video"],
                "name": "DJI Mini 4 Pro Drone with RC 2 Controller",
                "slug": "dji-mini-4-pro-drone-rc-2",
                "sku": "DJI-MINI4P-RC2",
                "brand": "DJI",
                "description": "Under 249g ultra-lightweight design. Omnidirectional obstacle sensing, 4K/60fps HDR True Vertical Shooting, up to 34 minutes flight time, and 20km FHD video transmission.",
                "short_description": "Under 249g drone with Omnidirectional Obstacle Sensing and 4K/60fps HDR video.",
                "price": 99990.00,
                "discount_price": 92990.00,
                "stock": 10,
                "average_rating": 4.80,
                "reviews_count": 8,
                "is_featured": False,
                "images": [
                    {"image_url": "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=800&q=80", "is_primary": True},
                ],
                "attributes": [
                    {"attribute_name": "Weight", "attribute_value": "< 249 grams"},
                    {"attribute_name": "Max Flight Time", "attribute_value": "34 Minutes"},
                ],
            },
        ]

        created_products = []
        for pdata in products_data:
            images = pdata.pop("images", [])
            attributes = pdata.pop("attributes", [])
            prod = Product(**pdata)
            db.session.add(prod)
            db.session.flush()

            for idx, img in enumerate(images):
                pimg = ProductImage(
                    product_id=prod.id,
                    image_url=img["image_url"],
                    alt_text=prod.name,
                    display_order=idx,
                    is_primary=img.get("is_primary", idx == 0),
                )
                db.session.add(pimg)

            for attr in attributes:
                pattr = ProductAttribute(
                    product_id=prod.id,
                    attribute_name=attr["attribute_name"],
                    attribute_value=attr["attribute_value"],
                )
                db.session.add(pattr)

            # Record initial inventory audit transaction
            OrderRepository.log_inventory(
                product_id=prod.id,
                change_quantity=prod.stock,
                balance_after=prod.stock,
                transaction_type="restock",
                notes="Initial inventory stock load",
                created_by=admin.id,
            )
            created_products.append(prod)

        db.session.flush()

        print("Seeding Coupons...")
        now = datetime.now(timezone.utc)
        coupons = [
            Coupon(
                code="WELCOME10",
                discount_type="percentage",
                discount_value=10.00,
                min_order_amount=2000.00,
                max_discount=2500.00,
                usage_limit=500,
                usage_count=0,
                is_active=True,
                starts_at=now - timedelta(days=1),
                expires_at=now + timedelta(days=365),
            ),
            Coupon(
                code="FESTIVE500",
                discount_type="fixed_amount",
                discount_value=500.00,
                min_order_amount=5000.00,
                usage_limit=1000,
                usage_count=0,
                is_active=True,
                starts_at=now - timedelta(days=1),
                expires_at=now + timedelta(days=180),
            ),
        ]
        db.session.add_all(coupons)

        print("Seeding Verified Customer Orders & Historical Interactions...")
        # Create a sample completed order for customer1 (Sony WH-1000XM5 + AirPods Pro)
        sony_prod = created_products[0]
        airpods_prod = created_products[2]

        order1 = Order(
            user_id=customer1.id,
            order_number="ORD-20261101-9B3E21",
            status="delivered",
            subtotal=49980.00,
            discount_amount=2500.00,
            tax_amount=8546.40,
            shipping_amount=0.00,
            total_amount=56026.40,
            coupon_code="WELCOME10",
            shipping_address_snapshot={
                "recipient_name": "Rahul Sharma",
                "phone": "+91 9812345678",
                "street_address": "Flat 402, Green Glen Layout, Bellandur",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560103",
                "country": "India",
            },
            created_at=now - timedelta(days=5),
        )
        db.session.add(order1)
        db.session.flush()

        item1 = OrderItem(
            order_id=order1.id,
            product_id=sony_prod.id,
            product_name=sony_prod.name,
            sku=sony_prod.sku,
            unit_price=sony_prod.effective_price,
            quantity=1,
            total_price=sony_prod.effective_price,
            created_at=now - timedelta(days=5),
        )
        item2 = OrderItem(
            order_id=order1.id,
            product_id=airpods_prod.id,
            product_name=airpods_prod.name,
            sku=airpods_prod.sku,
            unit_price=airpods_prod.effective_price,
            quantity=1,
            total_price=airpods_prod.effective_price,
            created_at=now - timedelta(days=5),
        )
        db.session.add_all([item1, item2])

        # Add genuine verified review for customer1's order
        rev1 = ProductReview(
            product_id=sony_prod.id,
            user_id=customer1.id,
            order_id=order1.id,
            rating=5,
            title="Exceptional active noise cancellation and comfort",
            comment="I use these daily in my office and during travel. The noise cancellation is the best I have ever tested, and the battery easily lasts multiple days of regular listening.",
            is_verified_purchase=True,
            is_approved=True,
            created_at=now - timedelta(days=3),
        )
        db.session.add(rev1)

        # Seed sample interaction events for recommendation baseline
        events = [
            UserInteraction(user_id=customer1.id, session_id="sess_1", product_id=sony_prod.id, interaction_type="view", dwell_time_seconds=95),
            UserInteraction(user_id=customer1.id, session_id="sess_1", product_id=sony_prod.id, interaction_type="cart_add"),
            UserInteraction(user_id=customer1.id, session_id="sess_1", product_id=sony_prod.id, interaction_type="purchase"),
            UserInteraction(user_id=customer1.id, session_id="sess_1", product_id=airpods_prod.id, interaction_type="view", dwell_time_seconds=60),
            UserInteraction(user_id=customer1.id, session_id="sess_1", product_id=airpods_prod.id, interaction_type="purchase"),
            UserInteraction(user_id=customer2.id, session_id="sess_2", product_id=created_products[3].id, interaction_type="view", dwell_time_seconds=140), # MacBook Pro
            UserInteraction(user_id=customer2.id, session_id="sess_2", product_id=created_products[3].id, interaction_type="wishlist_add"),
            UserInteraction(user_id=customer2.id, session_id="sess_2", product_id=created_products[5].id, interaction_type="view", dwell_time_seconds=80), # iPhone 15 Pro
        ]
        db.session.add_all(events)

        db.session.commit()
        print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
