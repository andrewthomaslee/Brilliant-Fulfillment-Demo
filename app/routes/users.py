# Standard Imports
from typing import Any
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse
from mohtml import div  # pyrefly: ignore
from beanie.operators import Set
from pydantic import ValidationError

# My Imports
from ..models import (
    User,
    UserGet,
    UserCreate,
    UserUpdate,
)


# ------------------Helpers-------------------#
async def validate_user(user: User | None) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/users",
    tags=["users"],
)


# -------------------User-Routes-------------------#
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserCreate) -> User:
    try:
        user = User(**user_request.model_dump())
        await user.create()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Request: {e}")
    return user


@router.get("/", response_model=list[User])
async def get_users() -> list[User]:
    users: list[User] = await User.find_all().to_list()
    return users


@router.get("/", response_model=list[User])
async def query_users(user_query: UserGet) -> list[User]:
    try:
        users: list[User] = await User.find(user_query.model_dump(exclude_unset=True)).to_list()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not found: {e}")
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str) -> User:
    try:
        user: User = await validate_user(await User.get(user_id))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not found: {e}")
    return user


@router.put("/{user_id}", response_model=User, status_code=status.HTTP_202_ACCEPTED)
async def update_user(user_id: str, user_request: UserUpdate) -> User:
    try:
        user: User = await validate_user(await User.get(user_id))
        await user.update(Set(user_request.model_dump(exclude_unset=True)))
        user = await validate_user(await User.get(user_id))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not found: {e}")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(user_id: str) -> str:
    try:
        user: User = await validate_user(await User.get(user_id))
        await user.delete()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not found: {e}")
    return f"User {user_id} deleted"
