def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "name": "John",
            "lastname": "Doe",
            "email": "john@example.com",
            "username": "john_doe",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "john_doe"
    assert data["name"] == "John"
    assert data["lastname"] == "Doe"
    assert data["email"] == "john@example.com"
    assert data["role"] == "admin"
    assert data["is_active"] is True

    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    user_data = {
        "name": "John",
        "lastname": "Doe",
        "email": "duplicate@example.com",
        "username": "user_one",
        "password": "password123",
    }

    response = client.post(
        "/users/register",
        json=user_data,
    )

    assert response.status_code == 201

    response = client.post(
        "/users/register",
        json={
            "name": "Jane",
            "lastname": "Doe",
            "email": "duplicate@example.com",
            "username": "user_two",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("User with this email already exists")


def test_register_duplicate_username(client):
    response = client.post(
        "/users/register",
        json={
            "name": "John",
            "lastname": "Doe",
            "email": "first@example.com",
            "username": "same_username",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/users/register",
        json={
            "name": "Jane",
            "lastname": "Doe",
            "email": "second@example.com",
            "username": "same_username",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("User with this username already exists")


def test_login_user(client):
    client.post(
        "/users/register",
        json={
            "username": "loginuser",
            "name": "Login",
            "lastname": "User",
            "email": "login@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/users/login",
        data={
            "username": "loginuser",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/users/register",
        json={
            "username": "wrongpass",
            "name": "Wrong",
            "lastname": "Password",
            "email": "wrongpass@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/users/login",
        data={
            "username": "wrongpass",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid login or password"


def test_get_me(client):
    client.post(
        "/users/register",
        json={
            "username": "me_user",
            "name": "Me",
            "lastname": "User",
            "email": "me@example.com",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/users/login",
        data={
            "username": "me_user",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "me_user"
    assert data["email"] == "me@example.com"
    assert data["name"] == "Me"
    assert data["lastname"] == "User"


def test_get_me_without_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_auth_headers(client, auth_headers):
    response = client.get(
        "/users/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_admin_can_change_user_role(
    client,
    admin_headers,
    second_user,
):
    response = client.patch(
        f"/users/{second_user['id']}/role",
        headers=admin_headers,
        json={
            "role": "moderator",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == second_user["id"]
    assert data["role"] == "moderator"


def test_admin_can_deactivate_user(
    client,
    admin_headers,
    second_user,
):
    response = client.patch(
        f"/users/{second_user['id']}/status",
        headers=admin_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_regular_user_cannot_change_role(
    client,
    second_user_headers,
    registered_user,
):
    response = client.patch(
        f"/users/{registered_user['id']}/role",
        headers=second_user_headers,
        json={
            "role": "moderator",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("Only admin can change user role")


def test_regular_user_cannot_change_status(
    client,
    second_user_headers,
    registered_user,
):
    response = client.patch(
        f"/users/{registered_user['id']}/status",
        headers=second_user_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("Only admin can change user status")
