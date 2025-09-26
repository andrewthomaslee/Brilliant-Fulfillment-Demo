# Standard Imports


# Third Party Imports
from fastapi import APIRouter, Request
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import DatastarResponse
from pydantic import BaseModel

# My Imports


class DarkMode(BaseModel):
    dark_mode: bool | None = None


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


# -------------------Settings-Routes-------------------#
@router.get("/dark_mode/", description="Toggle dark mode")
async def update_dark_mode(request: Request) -> DatastarResponse:
    if "dark_mode" not in request.session:
        request.session["dark_mode"] = True
    elif "dark_mode" in request.session:
        request.session["dark_mode"] = not request.session["dark_mode"]

    return DatastarResponse(
        [
            SSE.patch_elements(
                """<body id="base_body" class="{% if request.session.get('dark_mode') %} dark {% endif %} antialiased "></body>""",
            )
        ]
    )
