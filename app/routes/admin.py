# Standard Imports
from typing import Any
import logging
from logging import Logger

# Third Party Imports
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.templating import _TemplateResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode
from datastar_py.fastapi import DatastarResponse, read_signals
from beanie.operators import Set, RegEx, GTE, LTE, Eq, NE, LT, GT, NotIn  # noqa: F401
from jinja2 import Template

# My Imports
from ..utils import current_time
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
    MachineMissingLog,
)

logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


# ------------------Routes-------------------#
@router.get("/dashboard/")
async def dashboard(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("dashboard.html", {"request": request})
