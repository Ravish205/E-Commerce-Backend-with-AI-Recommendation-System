def test_interaction_tracking(client, customer_token):
    prod_res = client.get("/api/products/test-wireless-anc-headphones")
    prod_id = prod_res.get_json()["data"]["id"]

    res = client.post(
        "/api/recommendations/track-interaction",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "product_id": prod_id,
            "interaction_type": "view",
            "dwell_time_seconds": 45,
        },
    )
    assert res.status_code == 201
    assert res.get_json()["success"] is True

def test_trending_recommendations_and_out_of_stock_exclusion(client):
    res = client.get("/api/recommendations/trending")
    assert res.status_code == 200
    recommendations = res.get_json()["data"]
    assert len(recommendations) >= 1
    # Verify out of stock item (Test Vintage Audio Player) is NOT in recommendations
    for r in recommendations:
        assert r["stock"] > 0
        assert r["name"] != "Test Vintage Audio Player"

def test_similar_products_recommendations(client):
    prod_res = client.get("/api/products/test-wireless-anc-headphones")
    prod_id = prod_res.get_json()["data"]["id"]

    res = client.get(f"/api/recommendations/similar/{prod_id}")
    assert res.status_code == 200
    similar = res.get_json()["data"]
    # Should recommend Test Compact Studio Earbuds (both in Audio, both SoundCorp)
    assert len(similar) >= 1
    assert similar[0]["id"] != prod_id
    assert similar[0]["stock"] > 0
    assert "recommendation_reason" in similar[0]

def test_personalized_recommendations_cold_start(client):
    # Unauthenticated user with no interactions gets trending fallback
    res = client.get("/api/recommendations/personalized")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert isinstance(data, list)
    for item in data:
        assert item["stock"] > 0
