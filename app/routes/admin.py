# Standard Imports
from typing import Any
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse  # noqa: F401
from mohtml import div  # pyrefly: ignore
from beanie.operators import Set

# My Imports
from ..models.admin import User, UserRequest


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

# ------------------Routes-------------------#
# @router.get("/", response_class=HTMLResponse)
# async def read_index(request: Request) -> DatastarResponse:
#     return DatastarResponse(
#         [SSE.patch_elements(div(f"Hello World @ {datetime.now().isoformat()}"))]
#     )


# @router.post("/submit")
# async def submit_note(request: Request) -> None:
#     signals: dict[str, Any] | None = await read_signals(request)
#     print(signals)


@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserRequest) -> User:
    user = User(**user_request.model_dump())
    await user.create()
    return user


@router.get("/users", response_model=list[User])
async def get_users() -> list[User]:
    posts: list[User] = await User.find_all().to_list()
    return posts


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str) -> User:
    user: User = valid_user(await User.get(user_id))
    return user


@router.put("/{user_id}", response_model=User, status_code=status.HTTP_202_ACCEPTED)
async def update_user(user_id: str, user_request: UserRequest) -> User:
    user: User = valid_user(await User.get(user_id))
    await user.update(Set(user_request.model_dump(exclude_unset=True)))
    user = valid_user(await User.get(user_id))
    return user


@router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(user_id: str) -> str:
    user: User = valid_user(await User.get(user_id))
    await user.delete()
    return f"User {user_id} deleted"


def valid_user(user: User | None) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
