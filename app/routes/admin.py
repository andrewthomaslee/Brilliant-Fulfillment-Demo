# Standard Imports
from _hashlib import new
from typing import Any
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse  # noqa: F401
from mohtml import div  # pyrefly: ignore
from sqlmodel import Session, select


# My Imports
from ..db import get_session
from ..models.admin import Users, Machines


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


@router.get("/users", response_model=list[Users])
async def read_users(
    request: Request,
    session: Session = Depends(get_session),
) -> list[Users]:
    return session.query(Users).all()


@router.put("/users", response_model=Users, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user: Users,
    session: Session = Depends(get_session),
):
    try:
        new_user = Users(**user.model_dump())
        session.add(new_user)
        session.commit()
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )


@router.get("/machines", response_model=list[Machines])
async def read_machines(
    request: Request,
    session: Session = Depends(get_session),
) -> list[Users]:
    return session.query(Machines).all()


@router.put("/machines", response_model=Machines, status_code=status.HTTP_201_CREATED)
async def create_machine(
    request: Request,
    machine: Machines,
    session: Session = Depends(get_session),
):
    try:
        new_machine = Machines(**machine.model_dump())
        session.add(new_machine)
        session.commit()
        return new_machine
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )
