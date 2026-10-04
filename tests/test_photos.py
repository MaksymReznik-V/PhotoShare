from unittest.mock import patch


def test_upload_photo(client, auth_headers):
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

    data = response.json()

    assert data["url"] == "https://example.com/test.jpg"
    assert data["description"] == "Test photo"

    tag_names = [tag["name"] for tag in data["tags"]]

    assert "nature" in tag_names
    assert "travel" in tag_names


def test_upload_photo_without_auth(client):
    response = client.post(
        "/photos/load",
        files={
            "file": (
                "test.jpg",
                b"fake image content",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 401


def test_upload_non_image(client, auth_headers):
    response = client.post(
        "/photos/load",
        headers=auth_headers,
        files={
            "file": (
                "test.txt",
                b"not an image",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("File must be an image")


def test_upload_more_than_five_tags(
    client,
    auth_headers,
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
            "tags": "one,two,three,four,five,six",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Maximum 5 tags allowed")


def test_get_photo(client, photo):
    photo_id = photo["id"]

    response = client.get(
        f"/photos/{photo_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == photo_id
    assert data["description"] == "Test photo"
    assert data["url"] == "https://example.com/test.jpg"


def test_get_nonexistent_photo(client):
    response = client.get(
        "/photos/999999",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == ("Photo not found")


def test_update_own_photo(
    client,
    auth_headers,
    photo,
):
    response = client.put(
        f"/photos/{photo['id']}",
        headers=auth_headers,
        json={
            "description": "Updated description",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == photo["id"]
    assert data["description"] == "Updated description"


def test_delete_own_photo(
    client,
    auth_headers,
    photo,
):
    from unittest.mock import patch

    with patch("routers.photos.cloudinary.uploader.destroy") as mock_destroy:
        response = client.delete(
            f"/photos/{photo['id']}",
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["id"] == photo["id"]

    mock_destroy.assert_called_once_with("photoshare/test123")

    response = client.get(
        f"/photos/{photo['id']}",
    )

    assert response.status_code == 404


def test_cannot_update_another_users_photo(
    client,
    photo,
    second_user_headers,
):
    response = client.put(
        f"/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "description": "Hacked description",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You cannot edit this photo")


def test_cannot_delete_another_users_photo(
    client,
    photo,
    second_user_headers,
):
    response = client.delete(
        f"/photos/{photo['id']}",
        headers=second_user_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You cannot delete this photo")


def test_cannot_transform_another_users_photo(
    client,
    photo,
    second_user_headers,
):
    response = client.post(
        f"/photos/{photo['id']}/transform",
        headers=second_user_headers,
        params={
            "width": 500,
            "height": 500,
            "crop": "fill",
            "effect": "grayscale",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You cannot transform this photo")


def test_search_photos_by_tag(
    client,
    auth_headers,
    photo,
):
    response = client.get(
        "/photos/search/",
        headers=auth_headers,
        params={
            "tag": "nature",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == photo["id"]

    tag_names = [tag["name"] for tag in data[0]["tags"]]

    assert "nature" in tag_names


def test_search_photos_by_description(
    client,
    auth_headers,
    photo,
):
    response = client.get(
        "/photos/search/",
        headers=auth_headers,
        params={
            "description": "Test",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == photo["id"]
    assert data[0]["description"] == "Test photo"


def test_transform_own_photo(
    client,
    auth_headers,
    photo,
):
    with patch(
        "routers.photos.cloudinary.utils.cloudinary_url",
        return_value=(
            "https://example.com/transformed.jpg",
            {},
        ),
    ):
        response = client.post(
            f"/photos/{photo['id']}/transform",
            headers=auth_headers,
            params={
                "width": 500,
                "height": 400,
                "crop": "fill",
                "effect": "grayscale",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["url"] == ("https://example.com/transformed.jpg")
    assert data["photo_id"] == photo["id"]
