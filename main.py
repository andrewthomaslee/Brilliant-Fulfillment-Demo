#!/usr/bin/env python

# Standard Imports
from typing import Callable, Coroutine
from pathlib import Path
import subprocess
import logging
from logging import Logger
import os

# Third Party Imports
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from starlette.templating import _TemplateResponse
from starlette.middleware.sessions import SessionMiddleware
import marimo
from marimo._server.asgi import ASGIAppBuilder
from pydantic import BaseModel

# My Imports
from monotes import router

# ---------------Logging---------------#
logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ---------Setup-App---------------#
# Discover the base directory relative to this file
BASE_DIR: Path = Path(__file__).parent
MARIMO_DIR: Path = BASE_DIR / "pages"
# Create FastAPI app
app: FastAPI = FastAPI()
app.add_middleware(
    GZipMiddleware,  # pyrefly: ignore
    minimum_size=500,
    compresslevel=9,
)
# Add static files
app.mount(
    "/style",
    StaticFiles(directory=BASE_DIR / "style", follow_symlink=True),
    name="style",
)
# Create Jinja2 templates
templates: Jinja2Templates = Jinja2Templates(directory=BASE_DIR / "style" / "templates")


# ---------------Marimo-Pages---------------#
server: ASGIAppBuilder = (
    marimo.create_asgi_app()
    .with_app(path="/admin/dashboard", root=MARIMO_DIR / "dashboard")
    .with_app(path="/packer/questionaire", root=MARIMO_DIR / "questionaire")
)


# ----------Auth-----------#

users: dict[str, str] = {
    "admin": "password123"
}  ## TODO: Replace with actual authentication


class LoginForm(BaseModel):
    username: str
    password: str


def get_current_user(request: Request) -> str:
    username: str | None = request.session.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return username


# ----------Login-Routes-----------#


@app.middleware("http")
async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[None, None, Response]],
) -> Response:
    if request.url.path == "/login":
        return await call_next(request)

    if "username" not in request.session:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return await call_next(request)


@app.get("/login")
async def get_login(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def post_login(
    request: Request, username: str = Form(...), password: str = Form(...)
) -> RedirectResponse | _TemplateResponse:
    if username in users and password == users[username]:
        request.session["username"] = username
        logger.info(f"User {username} logged in successfully")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    logger.warning(f"Failed login attempt for user {username}")
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@app.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    username: str | None = request.session.get("username")
    request.session.clear()
    logger.info(f"User {username} logged out")
    return RedirectResponse(url="/login")


# ---------Default-Routes---------#
@app.get("/", response_class=HTMLResponse)
async def read_index(
    request: Request,
    username: str = Depends(get_current_user),
) -> _TemplateResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "username": username}
    )


@app.get("/favicon.ico")
async def favicon(request: Request) -> FileResponse:
    return FileResponse(BASE_DIR / "style" / "assets" / "favicon.ico")


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> _TemplateResponse:
    logger.error(f"HTTP error occurred: {exc.detail}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "detail": exc.detail},
        status_code=exc.status_code,
    )


# ---------API-Routes---------#
app.include_router(router)
app.mount("/", server.build())
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key")
)

if __name__ == "__main__":
    # Valkey setup
    Path(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
    subprocess.run(["valkey-server", "-d"], cwd=BASE_DIR / "data", check=True)

    # Database setup

    # FastAPI start
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7999,
        workers=3,
        timeout_graceful_shutdown=10,
        use_colors=True,
    )
