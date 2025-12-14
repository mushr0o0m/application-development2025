import pytest
from sqlalchemy import select


# Тест проверяет создание пользователя и возвращаемые поля (id, username, email)
@pytest.mark.asyncio
async def test_create_user(user_repository):
    user_data = {
        "username": "alice",
        "email": "alice@example.com",
        "description": "Test user",
    }

    user = await user_repository.create(user_data)

    assert user.id is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"


# Тест проверяет поиск пользователя по email через метод get_by_filter
@pytest.mark.asyncio
async def test_get_user_by_email(user_repository):
    user_data = {
        "username": "bob",
        "email": "bob@example.com",
    }
    await user_repository.create(user_data)

    results = await user_repository.get_by_filter(
        count=10, page=1, email="bob@example.com"
    )
    assert len(results) == 1
    assert results[0].email == "bob@example.com"


# Тест проверяет обновление полей пользователя (description)
@pytest.mark.asyncio
async def test_update_user(user_repository):
    user_data = {
        "username": "carol",
        "email": "carol@example.com",
    }

    user = await user_repository.create(user_data)

    updated = await user_repository.update(
        user.id, {"description": "updated description"}
    )
    assert updated.description == "updated description"


# Тест проверяет удаление пользователя и отсутствие в результате поиска по email
@pytest.mark.asyncio
async def test_delete_user(user_repository):
    user_data = {
        "username": "dave",
        "email": "dave@example.com",
    }

    user = await user_repository.create(user_data)
    await user_repository.delete(user.id)

    results = await user_repository.get_by_filter(
        count=10, page=1, email="dave@example.com"
    )
    assert len(results) == 0


# Тест проверяет получение списка пользователей (минимум 3 созданных)
@pytest.mark.asyncio
async def test_list_users(user_repository):
    # создаём несколько пользователей
    for i in range(3):
        await user_repository.create(
            {"username": f"u{i}", "email": f"u{i}@example.com"}
        )

    results = await user_repository.get_by_filter(count=10, page=1)
    assert len(results) >= 3
