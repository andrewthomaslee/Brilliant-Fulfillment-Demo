# Standard Imports
from typing import Any, Annotated
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse
from mohtml import div  # pyrefly: ignore

# My Imports
from ..config import templates


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


# -------------------Settings-Routes-------------------#
@router.put("/dark_mode/")
async def update_dark_mode(dark_mode: Annotated[bool, Query()]) -> DatastarResponse:
    if dark_mode:
        return DatastarResponse(
            content=[
                SSE.patch_elements(
                    """
                <body id="base_body" data-signals="{dark_mode: true}" data-class="{dark: $dark_mode}" class="{% block body_class %}{% endblock %}">
                """
                )
            ]
        )
    else:
        return DatastarResponse(
            content=[
                SSE.patch_elements(
                    """
                <body id="base_body" data-signals="{dark_mode: false}" data-class="{dark: $dark_mode}" class="{% block body_class %}{% endblock %}">
                """
                )
            ]
        )
