def test_rate_another_users_photo(
    client,
    second_user_headers,
    photo,
):
    response = client.post(
        f"/ratings/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "value": 5,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["photo_id"] == photo["id"]
    assert data["value"] == 5


def test_cannot_rate_own_photo(
    client,
    auth_headers,
    photo,
):
    response = client.post(
        f"/ratings/photos/{photo['id']}",
        headers=auth_headers,
        json={
            "value": 5,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You cannot rate your own photo")


def test_cannot_rate_same_photo_twice(
    client,
    second_user_headers,
    photo,
):
    first_response = client.post(
        f"/ratings/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "value": 4,
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/ratings/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "value": 5,
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == ("You have already rated this photo")


def test_get_photo_rating(
    client,
    second_user_headers,
    photo,
):
    create_response = client.post(
        f"/ratings/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "value": 4,
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/ratings/photos/{photo['id']}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["photo_id"] == photo["id"]
    assert data["average_rating"] == 4.0
    assert data["ratings_count"] == 1


def test_rate_nonexistent_photo(
    client,
    second_user_headers,
):
    response = client.post(
        "/ratings/photos/999999",
        headers=second_user_headers,
        json={
            "value": 5,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == ("Photo not found")


def test_regular_user_cannot_delete_rating(
    client,
    second_user_headers,
    photo,
):
    create_response = client.post(
        f"/ratings/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "value": 5,
        },
    )

    assert create_response.status_code == 201

    rating = create_response.json()

    response = client.delete(
        f"/ratings/{rating['id']}",
        headers=second_user_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You cannot delete ratings")
