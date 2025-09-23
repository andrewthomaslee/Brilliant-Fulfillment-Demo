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
    Machine,
    MachineGet,
    MachineCreate,
    MachineUpdate,
)


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/machines",
    tags=["machines"],
)


# -------------------Machine-Routes-------------------#
@router.post("/", response_model=Machine, status_code=status.HTTP_201_CREATED)
async def create_machine(machine_request: MachineCreate) -> Machine:
    try:
        machine = Machine(**machine_request.model_dump())
        await machine.create()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Request: {e}")
    return machine


@router.get("/", response_model=list[Machine])
async def get_machines() -> list[Machine]:
    machines: list[Machine] = await Machine.find_all().to_list()
    return machines


@router.get("/{machine_id}", response_model=Machine)
async def get_machine(machine_id: str) -> Machine:
    try:
        machine: Machine = valid_machine(await Machine.get(machine_id))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Machine not found: {e}")
    return machine


@router.put("/{machine_id}", response_model=Machine, status_code=status.HTTP_202_ACCEPTED)
async def update_machine(machine_id: str, machine_request: MachineUpdate) -> Machine:
    try:
        machine: Machine = valid_machine(await Machine.get(machine_id))
        await machine.update(Set(machine_request.model_dump(exclude_unset=True)))
        machine = valid_machine(await Machine.get(machine_id))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Machine not found: {e}")
    return machine


@router.delete("/{machine_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_machine(machine_id: str) -> str:
    try:
        machine: Machine = valid_machine(await Machine.get(machine_id))
        await machine.delete()
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Machine not found: {e}")
    return f"Machine {machine_id} deleted"


def valid_machine(machine: Machine | None) -> Machine:
    if machine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")
    return machine
