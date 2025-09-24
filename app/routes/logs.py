# Standard Imports
from typing import Any, Annotated
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse
from mohtml import div  # pyrefly: ignore
from beanie.operators import Set, GTE, LTE, RegEx, Eq
from pydantic import ValidationError

# My Imports
from ..models import (
    Log,
    LogQuery,
    LogCreate,
)


# ------------------Helpers-------------------#
async def validate_log(log: Log | None) -> Log:
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log


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


@router.get("/query/", response_model=list[Log])
async def query_logs(log_query: Annotated[LogQuery, Query()]) -> list[Log]:
    query_params: list[LTE | GTE | Eq] = []
    try:
        operator: type[GTE] | type[LTE] = GTE if log_query.gte else LTE
        query_params.append(operator(Log.ts, log_query.ts))

        if log_query.user is not None:
            query_params.append(Eq(Log.user, log_query.user))
        if log_query.machine is not None:
            query_params.append(Eq(Log.machine, log_query.machine))
        if log_query.active is not None:
            query_params.append(Eq(Log.active, log_query.active))
        if log_query.prompt is not None:
            query_params.append(Eq(Log.prompt, log_query.prompt))

        logs: list[Log] = await Log.find(*query_params).to_list()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
    return logs


@router.get("/by_name/", response_model=list[Log])
async def get_logs_by_name(
    machine_name: Annotated[str, Query(min_length=1)], user_name: Annotated[str, Query(min_length=1)]
) -> list[Log]:
    query_params: list = []
    try:
        if user_name:
            query_params.append(RegEx("user_name", user_name, "ixsm"))
        if machine_name:
            query_params.append(RegEx("machine_name", machine_name, "ixsm"))

        logs: list[Log] = await Log.find(*query_params).to_list()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
    return logs


@router.get("/{log_id}", response_model=Log)
async def get_log(log_id: str) -> Log:
    try:
        log: Log = await validate_log(await Log.get(log_id))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
    return log


@router.put("/{log_id}", response_model=Log, status_code=status.HTTP_202_ACCEPTED)
async def update_log(log_id: str, log_request: Log) -> Log:
    try:
        log: Log = await validate_log(await Log.get(log_id))
        await log.update(Set(log_request.model_dump(exclude_unset=True)))
        log = await validate_log(await Log.get(log_id))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
    return log


@router.delete("/{log_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_log(log_id: str) -> str:
    try:
        log: Log = await validate_log(await Log.get(log_id))
        await log.delete()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Log not found: {e}")
    return f"Log {log_id} deleted"
