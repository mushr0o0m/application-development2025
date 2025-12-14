
def test_create_get_update_delete_user(client):
    """Тестирует API CRUD для пользователей: создание, получение по id, обновление и удаление."""

    # создаём пользователя
    payload = {"username": "api_user", "email": "api_user@example.com", "description": "from api"}
    resp = client.post("/users", json=payload)
    assert resp.status_code == 201 or resp.status_code == 200
    data = resp.json()
    user_id = data.get("id")
    assert user_id is not None

    # получаем пользователя по id
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 200
    got = resp.json()
    assert got["email"] == "api_user@example.com"

    # обновляем пользователя
    update_payload = {"username": "api_user2", "email": "api_user@example.com", "description": "updated"}
    resp = client.put(f"/users/{user_id}", json=update_payload)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["username"] == "api_user2"

    # список пользователей
    resp = client.get("/users")
    assert resp.status_code == 200
    listing = resp.json()
    assert "users" in listing

    # удаляем пользователя
    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code in (200, 204)


def test_list_users_pagination(client):
    """Тестирует, что список пользователей возвращает структуру с полем users и total."""
    resp = client.get("/users?count=5&page=1")
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert "total" in data
