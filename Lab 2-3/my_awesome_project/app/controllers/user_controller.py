"""HTTP controller exposing user CRUD endpoints.

This module defines a Litestar `Controller` that delegates business logic to
the :class:`app.services.user_service.UserService`.
"""

from __future__ import annotations

from uuid import UUID

from litestar import Controller, Request, delete, get, post, put
from litestar.params import Parameter

from app.schemas import UserListResponse, UserResponse
from app.services.user_service import UserService


class UserController(Controller):
    """Controller for user endpoints mounted at `/users`."""

    path = "/users"

    @get("/{user_id:uuid}")
    async def get_user_by_id(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> UserResponse:
        """Return a single user by id or ``None`` when not found."""

        user = await user_service.get_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    @get()
    async def get_all_users(
        self,
        user_service: UserService,
        count: int = Parameter(default=50, ge=1),
        page: int = Parameter(default=1, ge=1),
    ) -> UserListResponse:
        """Return paginated list of users and total count."""

        users = await user_service.get_by_filter(count=count, page=page)
        total = await user_service.count()

        return UserListResponse(
            users=[UserResponse.model_validate(u) for u in users],
            total=total,
        )

    @post()
    async def create_user(
        self,
        user_service: UserService,
        request: Request,
    ) -> UserResponse:
        """Create a new user from request JSON and return it."""

        user_json = await request.json()
        user = await user_service.create(user_json)
        return UserResponse.model_validate(user)

    @delete("/{user_id:uuid}")
    async def delete_user(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> None:
        """Delete a user by its id."""

        await user_service.delete(user_id)

    @put("/{user_id:uuid}")
    async def update_user(
        self,
        user_service: UserService,
        user_id: UUID,
        request: Request,
    ) -> UserResponse:
        """Update an existing user from request JSON and return it."""

        user_json = await request.json()
        user = await user_service.update(user_id, user_json)
        return UserResponse.model_validate(user)
