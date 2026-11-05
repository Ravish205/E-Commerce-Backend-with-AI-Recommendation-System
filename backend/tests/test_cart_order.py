def test_cart_operations_and_calculations(client, customer_token):
    # 1. Fetch product
    prod_res = client.get("/api/products/test-wireless-anc-headphones")
    prod_id = prod_res.get_json()["data"]["id"]

    # 2. Add to cart
    res = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"product_id": prod_id, "quantity": 2},
    )
    assert res.status_code == 200
    cart_data = res.get_json()["data"]
    assert cart_data["items_count"] == 2
    # effective_price is 12000.00 * 2 = 24000.00
    assert cart_data["subtotal"] == 24000.00

    # 3. Apply coupon SAVE10 (10% off min 1000)
    res_coupon = client.get(
        "/api/cart?coupon_code=SAVE10",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    c_data = res_coupon.get_json()["data"]
    assert c_data["discount_amount"] == 2400.00
    # Taxable amount = 24000 - 2400 = 21600. Tax = 18% of 21600 = 3888.00. Free shipping (>= 1000)
    assert c_data["tax_amount"] == 3888.00
    assert c_data["shipping_amount"] == 0.00
    assert c_data["final_total"] == 25488.00

def test_add_to_cart_exceeding_stock_fails(client, customer_token):
    prod_res = client.get("/api/products/test-wireless-anc-headphones")
    prod_id = prod_res.get_json()["data"]["id"]

    # Stock is 10, try adding 15
    res = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"product_id": prod_id, "quantity": 15},
    )
    assert res.status_code == 400
    assert "stock" in res.get_json()["message"]

def test_order_checkout_lifecycle(client, customer_token):
    # 1. Add item to cart
    prod_res = client.get("/api/products/test-wireless-anc-headphones")
    prod_id = prod_res.get_json()["data"]["id"]
    client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"product_id": prod_id, "quantity": 1},
    )

    # 2. Place Order
    order_res = client.post(
        "/api/orders",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "shipping_address": {
                "recipient_name": "Test Customer",
                "phone": "+91 9999988888",
                "street_address": "42 Test Avenue",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560001",
                "country": "India",
            },
            "coupon_code": "SAVE10",
        },
    )
    assert order_res.status_code == 201
    order_data = order_res.get_json()["data"]
    order_id = order_data["id"]
    assert order_data["status"] == "pending"
    assert order_data["order_number"].startswith("ORD-")
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["unit_price"] == 12000.00

    # 3. Verify product stock was decremented from 10 to 9
    updated_prod = client.get(f"/api/products/{prod_id}").get_json()["data"]
    assert updated_prod["stock"] == 9

    # 4. Cancel order and verify stock is restored to 10
    cancel_res = client.post(
        f"/api/orders/{order_id}/cancel",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"reason": "Changed my mind"},
    )
    assert cancel_res.status_code == 200
    assert cancel_res.get_json()["data"]["status"] == "cancelled"

    restored_prod = client.get(f"/api/products/{prod_id}").get_json()["data"]
    assert restored_prod["stock"] == 10
