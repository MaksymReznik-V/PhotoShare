def test_create_comment(
    client,
    auth_headers,
    photo,
):
    response = client.post(
        f"/comments/photos/{photo['id']}",
        headers=auth_headers,
        json={
            "text": "Test comment",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["text"] == "Test comment"
    assert data["photo_id"] == photo["id"]


def test_update_own_comment(
    client,
    auth_headers,
    photo,
):
    create_response = client.post(
        f"/comments/photos/{photo['id']}",
        headers=auth_headers,
        json={
            "text": "Original comment",
        },
    )

    assert create_response.status_code == 201

    comment = create_response.json()

    response = client.put(
        f"/comments/{comment['id']}",
        headers=auth_headers,
        json={
            "text": "Updated comment",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == comment["id"]
    assert data["text"] == "Updated comment"


def test_create_comment_for_nonexistent_photo(
    client,
    auth_headers,
):
    response = client.post(
        "/comments/photos/999999",
        headers=auth_headers,
        json={
            "text": "Test comment",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == ("Photo not found")


def test_cannot_update_another_users_comment(
    client,
    auth_headers,
    second_user_headers,
    photo,
):
    create_response = client.post(
        f"/comments/photos/{photo['id']}",
        headers=auth_headers,
        json={
            "text": "Original comment",
        },
    )

    assert create_response.status_code == 201

    comment = create_response.json()

    response = client.put(
        f"/comments/{comment['id']}",
        headers=second_user_headers,
        json={
            "text": "Changed by another user",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You cannot edit this comment")


def test_regular_user_cannot_delete_comment(
    client,
    second_user_headers,
    photo,
):
    create_response = client.post(
        f"/comments/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "text": "Second user comment",
        },
    )

    assert create_response.status_code == 201

    comment = create_response.json()

    response = client.delete(
        f"/comments/{comment['id']}",
        headers=second_user_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You cannot delete comments")


def test_admin_can_delete_comment(
    client,
    admin_headers,
    second_user_headers,
    photo,
):
    create_response = client.post(
        f"/comments/photos/{photo['id']}",
        headers=second_user_headers,
        json={
            "text": "Comment to delete",
        },
    )

    assert create_response.status_code == 201

    comment = create_response.json()

    response = client.delete(
        f"/comments/{comment['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == comment["id"]
    assert data["text"] == "Comment to delete"
