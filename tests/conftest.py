import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from dependencies.database import get_db
from main import app

TEST_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5433/photoshare_test"
)

engine_test = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=engine_test,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    yield

    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db_session():
    connection = engine_test.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def user_data():
    return {
        "username": "testuser",
        "name": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "password": "password123",
    }


@pytest.fixture()
def registered_user(client, user_data):
    response = client.post(
        "/users/register",
        json=user_data,
    )

    assert response.status_code == 201

    return response.json()


@pytest.fixture()
def auth_headers(client, registered_user, user_data):
    response = client.post(
        "/users/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture()
def photo(client, auth_headers):
    from unittest.mock import patch

    fake_cloudinary_result = {
        "secure_url": "https://example.com/test.jpg",
        "public_id": "photoshare/test123",
    }

    with patch(
        "routers.photos.cloudinary.uploader.upload",
        return_value=fake_cloudinary_result,
    ):
        response = client.post(
            "/photos/load",
            headers=auth_headers,
            files={
                "file": (
                    "test.jpg",
                    b"fake image content",
                    "image/jpeg",
                ),
            },
            data={
                "description": "Test photo",
                "tags": "nature,travel",
            },
        )

    assert response.status_code == 201

    return response.json()


@pytest.fixture()
def second_user(
    client,
    registered_user,
):
    user_data = {
        "username": "seconduser",
        "name": "Second",
        "lastname": "User",
        "email": "second@example.com",
        "password": "password123",
    }

    response = client.post(
        "/users/register",
        json=user_data,
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"

    return response.json()


@pytest.fixture()
def admin_headers(client, registered_user, user_data):
    response = client.post(
        "/users/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture()
def second_user_headers(
    client,
    second_user,
):
    response = client.post(
        "/users/login",
        data={
            "username": "seconduser",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }
