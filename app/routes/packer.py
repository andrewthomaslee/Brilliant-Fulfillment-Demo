# Standard Imports
import logging
from logging import Logger

# Third Party Imports
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode
from datastar_py.fastapi import DatastarResponse
from beanie.operators import Set, RegEx, GTE, LTE, Eq, NE, LT, GT, NotIn  # noqa: F401
from jinja2 import Template

# My Imports
from ..config import templates
from ..models import (
    Machine,
    Log,
    Task,
    LogCreate,
    PromptCheckOut,
    PromptCheckIn,
    Prompt,
    MissingMachine,
    ActiveUsers,
    ActiveUsersMachinesProjection,
)

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
            SSE.patch_elements(html_content, mode=ElementPatchMode.REPLACE),
        ]
    )


@router.get("/check_out/get_machine/")
async def check_out_get_machine(request: Request) -> DatastarResponse:
    try:
        signals: dict[str, str] = dict()
        active_machines: list[ActiveUsersMachinesProjection] = (
            await ActiveUsers.find_all().project(ActiveUsersMachinesProjection).to_list()
        )
        print(active_machines)
        machine: Machine | None = await Machine.find_one(
            NotIn(Machine.name, active_machines),
            NotIn(Machine.name, request.session["missing_machines"]),
        )
        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

    except Exception as e:
        logger.error(f"Error during check out get machine: {e}")
        raise e

    signals["prompt_machine_name"] = machine.name
    return DatastarResponse([SSE.patch_signals(signals)])


@router.get("/check_out/report_missing_machine/")
async def check_out_report_missing_machine(
    request: Request, missing_machine: MissingMachine
) -> None:
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
async def check_out(request: Request, prompt_check_out: PromptCheckOut) -> RedirectResponse:
    try:
        valid_machine: Machine | None = await Machine.find_one(
            Machine.name == prompt_check_out.machine_name
        )
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
            machine={"id": valid_machine.id, "collection": "machines"},
            active=True,
            prompt=prompt_data,
        )

        create_activity: ActiveUsers = ActiveUsers(
            user_id=request["user_id"],
            username=request["username"],
            machine_name=valid_machine.name,
            task=prompt_check_out.task,
        )

        await create_activity.create()
        await Log(**log_create.model_dump(exclude_unset=True)).create()

    except Exception as e:
        logger.error(f"Error durining check out: {e}")
        raise e

    logger.info(
        f"Check out successful for user `{request['username']}:{request['user_id']}` with machine `{prompt_check_out.machine_name}`"
    )
    return RedirectResponse(url="/")


@router.get("/check_in/")
async def check_in_form(request: Request) -> DatastarResponse:
    template: Template = templates.get_template("check_in.html")
    html_content: str = template.render({"request": request})
    return DatastarResponse([SSE.patch_elements(html_content, mode=ElementPatchMode.REPLACE)])


@router.post("/check_in/", status_code=status.HTTP_201_CREATED)
async def check_in(request: Request, prompt_check_in: PromptCheckIn) -> RedirectResponse:
    try:
        # Sanity check
        valid_machine: Machine | None = await Machine.find_one(
            Machine.name == prompt_check_in.machine_name
        )
        if valid_machine is None:
            logger.error(f"Machine not found: {prompt_check_in.machine_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Machine not found")

        activity: ActiveUsers | None = await ActiveUsers.find_one(
            ActiveUsers.user_id == request["user_id"]
        )
        if activity is None:
            logger.error(f"Active user not found: {request['user_id']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Active user not found"
            )

        if activity.machine_name != valid_machine.name:
            logger.error(f"Machine name mismatch: {activity.machine_name=} != {valid_machine.name=}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Machine ID mismatch"
            )

        if activity.user_id != request["user_id"]:
            logger.error(f"User ID mismatch: {activity.user_id=} != {request['user_id']=}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID mismatch")

        prompt_data: Prompt = Prompt(
            condition=prompt_check_in.condition,
            battery=prompt_check_in.battery,
            task=activity.task,
            special_note=prompt_check_in.special_note,
        )

        create_log = LogCreate(
            user={"id": request["user_id"], "collection": "users"},
            machine={"id": valid_machine.id, "collection": "machines"},
            active=False,
            prompt=prompt_data,
        )

        check_in_log: Log = await Log(**create_log.model_dump(exclude_unset=True)).create()
        await activity.delete()
    except Exception as e:
        logger.error(f"Error during check in: {e}")
        raise e
    logger.info(
        f"Check in successful for user `{request['username']}:{request['user_id']}` with machine `{valid_machine.id}` with log : `{check_in_log}`"
    )

    return RedirectResponse(url="/")
