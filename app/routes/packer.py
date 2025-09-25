# Standard Imports
import logging
import json
from logging import Logger
from typing import Any

# Third Party Imports
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode
from datastar_py.fastapi import DatastarResponse
from beanie.operators import Set, RegEx, GTE, LTE, Eq, NE, LT, GT, NotIn  # noqa: F401
from valkey import Valkey
from jinja2 import Template

# My Imports
from ..db import get_valkey
from ..config import templates

from ..models import Machine, Log, Task, LogCreate, PromptCheckOut, PromptCheckIn, Prompt, MissingMachine

logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/packer",
    tags=["packer"],
)


# ------------------Routes-------------------#
@router.get("/check_out/")
async def check_out_form(request: Request) -> DatastarResponse:
    template: Template = templates.get_template("check_out.html")
    html_content: str = template.render({"request": request, "tasks": Task})
    return DatastarResponse(
        [
            SSE.patch_elements(html_content, use_view_transitions=True, mode=ElementPatchMode.REPLACE),
        ]
    )


@router.get("/check_out/get_machine/")
async def check_out_get_machine(request: Request, kv: Valkey = Depends(get_valkey)) -> DatastarResponse:
    try:
        signals: dict[str, str] = dict()
        machine_keys_with_prefix: list[bytes] = await kv.keys("machines:*")
        machine_keys: list[str] = [key.decode("utf-8").split(":", 1)[1] for key in machine_keys_with_prefix]

        # sanity check
        result: Any = ""
        try:
            result = await kv.get(f"users:{request['user_id']}")
        except Exception:
            logger.debug(f"{request['user_id']} not found in KV (Good!) {result=}")
            pass

        if "missing_machines" in request.session:
            missing_machines: list[str] = request.session["missing_machines"]
            machine: Machine | None = await Machine.find_one(
                NotIn(Machine.name, missing_machines), NotIn(Machine.name, machine_keys)
            )
        else:
            machine: Machine | None = await Machine.find_one(NotIn(Machine.name, machine_keys))
        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        signals["prompt_machine_name"] = machine.name

    except Exception as e:
        logger.error(f"Error during check out get machine: {e}")
        raise e

    return DatastarResponse([SSE.patch_signals(signals)])


@router.get("/check_out/report_missing_machine/")
async def check_out_report_missing_machine(request: Request, missing_machine: MissingMachine) -> None:
    try:
        if "missing_machines" not in request.session:
            request.session["missing_machines"] = [missing_machine.machine_name]
        else:
            request.session["missing_machines"].append(missing_machine.machine_name)
    except Exception as e:
        logger.error(f"Error during report missing machine: {e}")
        raise e
    logger.info(f"Reported missing machine: {missing_machine.machine_name}")
    return None


@router.post("/check_out/", response_model=LogCreate, status_code=status.HTTP_201_CREATED)
async def check_out(request: Request, prompt_check_out: PromptCheckOut, kv: Valkey = Depends(get_valkey)) -> Log:
    try:
        valid_machine: Machine | None = await Machine.find_one(Machine.name == prompt_check_out.machine_name)
        if valid_machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        prompt_data: Prompt = Prompt(
            condition=prompt_check_out.condition,
            battery=prompt_check_out.battery,
            task=prompt_check_out.task,
            special_note=prompt_check_out.special_note,
        )
        log_create: LogCreate = LogCreate(
            user={"id": request["user_id"], "collection": "users"},
            machine={"id": prompt_check_out.machine_name, "collection": "machines"},
            active=True,
            prompt=prompt_data,
        )

        result: Log = await Log(**log_create.model_dump(exclude_unset=True)).create()
        await kv.set(f"machines:{prompt_check_out.machine_name}", result, nx=True)
        await kv.set(f"users:{request['user_id']}", prompt_check_out.machine_name, nx=True)
    except Exception as e:
        logger.error(f"Error durining check out: {e}")
        raise e

    logger.info(
        f"Check out successful for user `{request['username']}:{request['user_id']}` with machine `{prompt_check_out.machine_name}`"
    )
    return result


@router.get("/check_in/")
async def check_in_form(request: Request) -> DatastarResponse:
    template: Template = templates.get_template("check_in.html")
    html_content: str = template.render({"request": request})
    return DatastarResponse(
        [SSE.patch_elements(html_content, use_view_transitions=True, mode=ElementPatchMode.REPLACE)]
    )


@router.post("/check_in/", status_code=status.HTTP_201_CREATED)
async def check_in(request: Request, prompt_check_in: PromptCheckIn, kv: Valkey = Depends(get_valkey)) -> Log:
    try:
        check_out_log = await kv.get(f"machines:{prompt_check_in.machine_name}")
        if check_out_log is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active Machine not found in KV")
        out_machine = await kv.get(f"users:{request['user_id']}")
        if out_machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in KV")

        prev_log: dict[str, Any] = json.loads(check_out_log)
        logger.info(f"Check out log: {prev_log}")

        # Sanity check
        valid_machine: Machine | None = await Machine.find_one(Machine.name == prompt_check_in.machine_name)
        if valid_machine is None:
            logger.error(f"Machine not found: {prompt_check_in.machine_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")
        if prev_log["machine"]["id"] != valid_machine.id:
            logger.error(f"Machine ID mismatch: {prev_log['machine']['id']=} != {valid_machine.id=}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine name mismatch")
        if prev_log["user"]["id"] != request["user_id"]:
            logger.error(f"User ID mismatch: {prev_log['user']['id']=} != {request['user_id']=}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User ID mismatch")
        if prev_log["user"]["id"] != out_machine:
            logger.error(f"User ID mismatch: {prev_log['user']['id']=} != {out_machine=}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User ID mismatch")

        prompt_data: Prompt = Prompt(
            condition=prompt_check_in.condition,
            battery=prompt_check_in.battery,
            task=prev_log["prompt"]["task"],
            special_note=prompt_check_in.special_note,
        )

        create_log = LogCreate(
            user={"id": request["user_id"], "collection": "users"},
            machine={"id": prompt_check_in.machine_name, "collection": "machines"},
            active=False,
            prompt=prompt_data,
        )

        check_in_log: Log = await Log(create_log.model_dump(exclude_unset=True)).create()
        kv.delete(f"machines:{prompt_check_in.machine_name}")
        checked_in_machine = await kv.getdel(f"users:{request['user_id']}")
    except Exception as e:
        logger.error(f"Error during check in: {e}")
        raise e
    logger.info(
        f"Check in successful for user `{request['username']}:{request['user_id']}` with machine `{checked_in_machine}` with log : `{check_in_log}`"
    )

    return RedirectResponse(url="/")
