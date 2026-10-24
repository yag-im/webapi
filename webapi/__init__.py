import json
import logging
import os
import typing as t
from pathlib import Path

from fastapi import (
    FastAPI,
    Request,
    Response,
)
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import URL
from starlette.middleware.sessions import SessionMiddleware

from webapi.api.account import bp as account_bp
from webapi.api.app import bp as app_bp
from webapi.api.auth import bp as auth_bp
from webapi.api.cluster import bp as cluster_bp
from webapi.biz import (
    errors,
    log_handler,
)
from webapi.proxy_fix import ProxyFixMiddleware
from webapi.sqldb import init_db

log = logging.getLogger("webapi")

BEHIND_PROXY = os.environ.get("BEHIND_PROXY", "false").lower() == "true"
STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    log_handler.init()
    init_db(
        URL.create(
            "postgresql+psycopg",
            username=os.environ["SQLDB_USERNAME"],
            password=os.environ["SQLDB_PASSWORD"],
            host=os.environ["SQLDB_HOST"],
            port=int(os.environ["SQLDB_PORT"]),
            database=os.environ["SQLDB_DBNAME"],
        ),
        json.loads(os.environ.get("SQLDB_ENGINE_OPTIONS", "{}")),
    )

    app = FastAPI(title="webapi", version="1.0.0", openapi_url="/api/specs/", docs_url=None, redoc_url=None)
    errors.init_app(app)

    app.include_router(account_bp)
    app.include_router(app_bp)
    app.include_router(auth_bp)
    app.include_router(cluster_bp)
    app.mount("/api/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/api/docs/", include_in_schema=False)
    def api_docs(request: Request) -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=str(request.url_for("openapi")),
            title="webapi",
            swagger_js_url=str(request.url_for("static", path="js/swagger-ui-bundle.js")),
            swagger_css_url=str(request.url_for("static", path="css/swagger-ui.css")),
            swagger_favicon_url=str(request.url_for("static", path="img/favicon-32x32.png")),
        )

    @app.middleware("http")
    async def log_request(request: Request, call_next: t.Callable[[Request], t.Awaitable[Response]]) -> Response:
        log.info("%s %s", request.method, request.url)
        log.info(request.headers)
        return await call_next(request)

    # user auth: signed cookie based session
    app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"], max_age=None, same_site="lax")
    # must be the outermost middleware
    if BEHIND_PROXY:
        app.add_middleware(ProxyFixMiddleware)

    return app
