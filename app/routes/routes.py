# Standard Imports
from typing import Any
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse  # noqa: F401
from mohtml import div  # pyrefly: ignore


# My Imports


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/questionaire",
    tags=["questionaire"],
)


# ------------------Routes-------------------#
@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> DatastarResponse:
    return DatastarResponse(
        [SSE.patch_elements(div(f"Hello World @ {datetime.now().isoformat()}"))]
    )


@router.post("/submit")
async def submit_note(request: Request) -> None:
    signals: dict[str, Any] | None = await read_signals(request)
    print(signals)
