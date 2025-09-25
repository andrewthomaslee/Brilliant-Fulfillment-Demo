# Standard Imports
from typing import Any, Annotated
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.templating import _TemplateResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse
from mohtml import div  # pyrefly: ignore
from pydantic import BaseModel

# My Imports
from ..config import templates


class DarkMode(BaseModel):
    dark_mode: bool | None = None


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


# -------------------Settings-Routes-------------------#
@router.get("/dark_mode/", description="Toggle dark mode")
async def update_dark_mode(request: Request) -> RedirectResponse:
    if "dark_mode" not in request.session:
        request.session["dark_mode"] = True
    elif "dark_mode" in request.session:
        request.session["dark_mode"] = not request.session["dark_mode"]

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
