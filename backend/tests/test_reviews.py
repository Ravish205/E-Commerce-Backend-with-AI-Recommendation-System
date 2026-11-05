def test_review_submission_and_rating_recalculation(client, customer_token):
    prod_res = client.get("/api/products/test-wireless-anc-headphones")
    prod_id = prod_res.get_json()["data"]["id"]

    # Submit a 5-star review
    res = client.post(
        "/api/reviews",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "product_id": prod_id,
            "rating": 5,
            "title": "Outstanding audio quality",
            "comment": "The active noise cancellation is top notch and the battery lasts as advertised.",
        },
    )
    assert res.status_code == 201
    assert res.get_json()["data"]["rating"] == 5

    # Check that product's average_rating and reviews_count updated
    updated_prod = client.get(f"/api/products/{prod_id}").get_json()["data"]
    assert updated_prod["average_rating"] == 5.0
    assert updated_prod["reviews_count"] == 1
