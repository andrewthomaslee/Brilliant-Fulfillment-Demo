#!/usr/bin/env python

# Standard Imports
from typing import Callable, Coroutine
from pathlib import Path
import logging
from logging import Logger
import os

# Third Party Imports
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
from starlette.templating import _TemplateResponse
from starlette.middleware.sessions import SessionMiddleware
import marimo
from marimo._server.asgi import ASGIAppBuilder

# My Imports


# ---------------Logging---------------#
logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ---------Setup-App---------------#
# Discover the base directory relative to this file
BASE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = Path(".." / BASE_DIR / "data")
MARIMO_DIR: Path = BASE_DIR / "pages"
# Create FastAPI app
app: FastAPI = FastAPI()
app.add_middleware(
    GZipMiddleware,  # pyrefly: ignore
    minimum_size=1000,
    compresslevel=5,
)
# Add static files
app.mount(
    "/style",
    StaticFiles(
        directory=BASE_DIR / "style", follow_symlink=True, check_dir=True, html=True
    ),
    name="style",
)
# Create Jinja2 templates
templates: Jinja2Templates = Jinja2Templates(directory=BASE_DIR / "style" / "templates")


# ----------Auth-----------#
users: dict[str, str] = {"admin": "admin"}  ## TODO: Replace with actual authentication


def get_current_user(request: Request) -> str:
    username: str | None = request.session.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return username


# ----------Auth-Middleware-----------#
@app.middleware("http")
async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[None, None, Response]],
) -> Response:
    excluded_paths: list[str] = [
        "/login",
        "/style/output.css",
        "/health",
        "/style/assets/favicon.ico",
    ]
    if any(request.url.path.startswith(path) for path in excluded_paths):
        return await call_next(request)

    if "username" not in request.session:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return await call_next(request)


# ----------Login-Routes-----------#
@app.get("/login")
async def get_login(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_model=None)
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


# ---------------Marimo-Pages---------------#
server: ASGIAppBuilder = (
    marimo.create_asgi_app()
    .with_app(path="/dashboard", root=str(MARIMO_DIR / "dashboard.py"))
    .with_app(path="/questionaire", root=str(MARIMO_DIR / "questionaire.py"))
)

# ---------App-Routers-&-Mounts-&-Middleware---------#
# app.include_router(router)
app.mount("/", server.build())
app.add_middleware(
    SessionMiddleware,  # pyrefly: ignore
    secret_key=os.getenv("SECRET_KEY", "your-secret-key"),
)
