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
    Log,
    LogGet,
    LogCreate,
)


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/logs",
    tags=["logs"],
)


# -------------------Log-Routes-------------------#
@router.post("/", response_model=Log, status_code=status.HTTP_201_CREATED)
async def create_log(log_request: LogCreate) -> Log:
    try:
        log = Log(**log_request.model_dump())
        await log.create()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Request: {e}")
    return log


@router.get("/", response_model=list[Log])
async def get_logs() -> list[Log]:
    logs: list[Log] = await Log.find_all().to_list()
    return logs


@router.get("/{log_id}", response_model=Log)
async def get_log(log_id: str) -> Log:
    try:
        log: Log = valid_log(await Log.get(log_id))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
    return log


# @router.put("/{log_id}", response_model=Log, status_code=status.HTTP_202_ACCEPTED)
# async def update_log(log_id: str, log_request: LogRequest) -> Log:
#     try:
#         log: Log = valid_log(await Log.get(log_id))
#         await log.update(Set(log_request.model_dump(exclude_unset=True)))
#         log = valid_log(await Log.get(log_id))
#     except ValidationError as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
#     return log


# @router.delete("/{log_id}", status_code=status.HTTP_202_ACCEPTED)
# async def delete_log(log_id: str) -> str:
#     try:
#         log: Log = valid_log(await Log.get(log_id))
#         await log.delete()
#     except ValidationError as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
#     return f"Log {log_id} deleted"


def valid_log(log: Log | None) -> Log:
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log
