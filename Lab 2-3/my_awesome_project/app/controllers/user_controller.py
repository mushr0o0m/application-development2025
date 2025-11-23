from __future__ import annotations

from typing import List
from uuid import UUID

from litestar import Controller, get, post, put, delete, Parameter, Provide
from litestar.exceptions import NotFoundException

from app.services.user_service import UserService
from app.schemas import UserCreate, UserResponse, UserListResponse


class UserController(Controller):
    path = "/users"
    dependencies = {"user_service": Provide("user_service")}

    @get("/{user_id:uuid}")
    async def get_user_by_id(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> UserResponse:
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
        users = await user_service.get_by_filter(count=count, page=page)
        total = await user_service.count()
        return UserListResponse(
            users=[UserResponse.model_validate(u) for u in users],
            total=total
        )

    @post()
    async def create_user(
        self,
        user_service: UserService,
        user_data: UserCreate,
    ) -> UserResponse:
        user = await user_service.create(user_data.model_dump())
        return UserResponse.model_validate(user)

    @delete("/{user_id:uuid}")
    async def delete_user(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> None:
        await user_service.delete(user_id)

    @put("/{user_id:uuid}")
    async def update_user(
        self,
        user_service: UserService,
        user_id: UUID,
        user_data: UserCreate,
    ) -> UserResponse:
        user = await user_service.update(user_id, user_data.model_dump())
        return UserResponse.model_validate(user)
