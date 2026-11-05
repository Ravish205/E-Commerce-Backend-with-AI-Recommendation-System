def test_user_registration(client):
    res = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "first_name": "New",
        "last_name": "User",
        "phone_number": "+91 9988776655",
    })
    assert res.status_code == 201
    json_data = res.get_json()
    assert json_data["success"] is True
    assert "access_token" in json_data["data"]
    assert json_data["data"]["user"]["email"] == "newuser@example.com"

def test_duplicate_registration_fails(client):
    res = client.post("/api/auth/register", json={
        "email": "customer.test@example.com",
        "password": "SecurePassword123!",
        "first_name": "Duplicate",
        "last_name": "User",
    })
    assert res.status_code == 400
    assert "already exists" in res.get_json()["message"]

def test_user_login_success(client):
    res = client.post("/api/auth/login", json={
        "email": "customer.test@example.com",
        "password": "CustomerPass123!",
    })
    assert res.status_code == 200
    assert res.get_json()["success"] is True
    assert "access_token" in res.get_json()["data"]

def test_user_login_invalid_password(client):
    res = client.post("/api/auth/login", json={
        "email": "customer.test@example.com",
        "password": "WrongPassword!",
    })
    assert res.status_code == 401
    assert res.get_json()["success"] is False

def test_protected_profile_endpoint(client, customer_token):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {customer_token}"})
    assert res.status_code == 200
    assert res.get_json()["data"]["email"] == "customer.test@example.com"

def test_admin_route_forbidden_for_customer(client, customer_token):
    res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {customer_token}"})
    assert res.status_code == 403

def test_admin_route_allowed_for_admin(client, admin_token):
    res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert "total_customers" in res.get_json()["data"]
