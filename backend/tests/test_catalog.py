def test_get_categories(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) >= 1
    assert data[0]["slug"] == "audio-electronics"

def test_get_products_list_and_search(client):
    # Search for Headphones
    res = client.get("/api/products?search=Headphones")
    assert res.status_code == 200
    products = res.get_json()["data"]
    assert len(products) == 1
    assert "Headphones" in products[0]["name"]

def test_get_product_detail(client):
    res = client.get("/api/products/test-wireless-anc-headphones")
    assert res.status_code == 200
    prod = res.get_json()["data"]
    assert prod["sku"] == "TST-ANC-01"
    assert prod["effective_price"] == 12000.00
    assert prod["is_in_stock"] is True

def test_admin_create_product(client, admin_token):
    cat_res = client.get("/api/categories")
    cat_id = cat_res.get_json()["data"][0]["id"]

    res = client.post(
        "/api/admin/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "category_id": cat_id,
            "name": "New High End Soundbar",
            "sku": "SND-BAR-09",
            "brand": "SoundCorp",
            "description": "Premium Dolby Atmos soundbar with wireless subwoofer.",
            "price": 34990.00,
            "discount_price": 29990.00,
            "stock": 15,
        },
    )
    assert res.status_code == 201
    assert res.get_json()["data"]["name"] == "New High End Soundbar"
