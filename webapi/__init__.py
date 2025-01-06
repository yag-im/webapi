import logging
import os

from flask import (
    Flask,
    request,
)
from werkzeug.middleware.proxy_fix import ProxyFix

from webapi.api import apispec
from webapi.api.account import bp as account_bp
from webapi.api.app import bp as app_bp
from webapi.api.auth import bp as auth_bp
from webapi.api.auth import discord_bp as auth_discord_bp
from webapi.api.auth import google_bp as auth_google_bp
from webapi.api.auth import login_manager
from webapi.api.auth import reddit_bp as auth_reddit_bp
from webapi.api.auth import twitch_bp as auth_twitch_bp
from webapi.biz import (
    errors,
    log_handler,
)
from webapi.sqldb import sqldb

log = logging.getLogger("webapi")

BEHIND_PROXY = os.environ.get("BEHIND_PROXY", "false").lower() == "true"


def create_app() -> Flask:
    app = Flask(__name__, static_url_path="/api/static")
    app.config.from_prefixed_env()
    # composite config parameters
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f'postgresql://{os.environ["SQLDB_USERNAME"]}:{os.environ["SQLDB_PASSWORD"]}@{os.environ["SQLDB_HOST"]}:\
        {os.environ["SQLDB_PORT"]}/{os.environ["SQLDB_DBNAME"]}'
    )

    # initialize flask extensions
    login_manager.init_app(app)
    sqldb.init_app(app)
    errors.init_app(app)
    log_handler.init_app(app)

    if BEHIND_PROXY:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # register blueprints
    app.register_blueprint(account_bp)
    app.register_blueprint(app_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_google_bp, url_prefix="/auth/login")
    app.register_blueprint(auth_discord_bp, url_prefix="/auth/login")
    app.register_blueprint(auth_reddit_bp, url_prefix="/auth/login")
    app.register_blueprint(auth_twitch_bp, url_prefix="/auth/login")

    # this must come after blueprints registration
    apispec.init_app(app)

    # pylint: disable=pointless-string-statement

    @app.before_request
    def log_request() -> None:
        log.info(request.__dict__)
        log.info(request.headers)

    return app
