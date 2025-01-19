import os
import typing as t
from http import HTTPStatus

import flask
from flask import (
    Blueprint,
    Response,
    abort,
)
from flask import current_app as app
from flask import (
    redirect,
    request,
    url_for,
)
from flask_dance.consumer import (
    oauth_authorized,
    oauth_before_login,
)
from flask_dance.consumer.oauth2 import OAuth2ConsumerBlueprint
from flask_dance.contrib.discord import (
    discord,
    make_discord_blueprint,
)
from flask_dance.contrib.google import (
    google,
    make_google_blueprint,
)
from flask_dance.contrib.reddit import (
    make_reddit_blueprint,
    reddit,
)
from flask_dance.contrib.twitch import (
    make_twitch_blueprint,
    twitch,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy.orm.exc import NoResultFound

from webapi.api.const import HTTP_HEADER_X_AUTH_UID
from webapi.models.account import UserDAO
from webapi.models.auth import FlaskDanceOauth
from webapi.sqldb import sqldb

SIGSVC_AUTH_TOKEN = os.environ["SIGSVC_AUTH_TOKEN"]

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str) -> UserDAO:
    return UserDAO.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized() -> None:
    abort(HTTPStatus.UNAUTHORIZED)


google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
    ],
)

discord_bp = make_discord_blueprint(
    client_id=os.getenv("DISCORD_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("DISCORD_OAUTH_CLIENT_SECRET"),
    scope=["identify", "email"],
)

reddit_bp = make_reddit_blueprint(
    client_id=os.getenv("REDDIT_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_OAUTH_CLIENT_SECRET"),
    scope=["identity"],  # reddit does not expose the user's email to 3rd parties
)

twitch_bp = make_twitch_blueprint(
    client_id=os.getenv("TWITCH_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("TWITCH_OAUTH_CLIENT_SECRET"),
    scope=["user:read:email"],
)


def create_user_and_login(
    bp_name: str, token: t.Dict, user_id: str, user_email: t.Optional[str] = None, user_name: t.Optional[str] = None
) -> bool:
    query = FlaskDanceOauth.query.filter_by(
        provider=bp_name,
        provider_user_id=user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = FlaskDanceOauth(
            provider=bp_name,
            provider_user_id=user_id,
            token=token,
        )
    if oauth.user is None:
        # If this OAuth token doesn't have an associated local account,
        # create a new local user account for this user. We can log
        # in that account as well, while we're at it.
        user = UserDAO(
            # Remember that `email` can be None, e.g. if the user declines
            # to publish their email address on Google!
            email=user_email,
            name=user_name,
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        sqldb.session.add_all([user, oauth])
        sqldb.session.commit()
    if login_user(oauth.user):
        app.logger.debug(f"successfully signed in with {bp_name}.")
    else:
        app.logger.warn(f"user {user_name} can't be signed in (is user active?).")

    next_url = flask.session["next_url"]

    # Since we're manually creating the OAuth model in the database,
    # we should return False so that Flask-Dance knows that
    # it doesn't have to do it. If we don't return False, the OAuth token
    # could be saved twice, or Flask-Dance could throw an error when
    # trying to incorrectly save it for us.
    return flask.redirect(next_url) if next_url else False


@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint: OAuth2ConsumerBlueprint, token: t.Dict) -> bool:
    if not token:
        app.logger.error("failed to log in with google")
        return False
    resp = blueprint.session.get("/oauth2/v3/userinfo")
    if not resp.ok:
        app.logger.error("failed to fetch user info from google")
        return False
    user_info = resp.json()
    return create_user_and_login(
        bp_name=blueprint.name, token=token, user_id=str(user_info["sub"]), user_email=user_info["email"]
    )


@oauth_authorized.connect_via(discord_bp)
def discord_logged_in(blueprint: OAuth2ConsumerBlueprint, token: t.Dict) -> bool:
    if not token:
        app.logger.error("failed to log in with discord")
        return False
    resp = blueprint.session.get("/api/users/@me")
    if not resp.ok:
        app.logger.error("failed to fetch user info from discord")
        return False
    user_info = resp.json()
    return create_user_and_login(
        bp_name=blueprint.name,
        token=token,
        user_id=str(user_info["id"]),
        user_email=user_info["email"],
        user_name=user_info["username"],
    )


@oauth_authorized.connect_via(reddit_bp)
def reddit_logged_in(blueprint: OAuth2ConsumerBlueprint, token: t.Dict) -> bool:
    if not token:
        app.logger.error("failed to log in with reddit")
        return False
    resp = blueprint.session.get("/api/v1/me")
    if not resp.ok:
        app.logger.error("failed to fetch user info from reddit")
        return False
    user_info = resp.json()
    return create_user_and_login(
        bp_name=blueprint.name, token=token, user_id=str(user_info["id"]), user_name=user_info["name"]
    )


@oauth_authorized.connect_via(twitch_bp)
def twitch_logged_in(blueprint: OAuth2ConsumerBlueprint, token: t.Dict) -> bool:
    if not token:
        app.logger.error("failed to log in with twitch")
        return False
    resp = blueprint.session.get("/helix/users")
    if not resp.ok:
        app.logger.error("failed to fetch user info from twitch")
        return False
    user_info = resp.json()["data"][0]
    return create_user_and_login(
        bp_name=blueprint.name,
        token=token,
        user_id=str(user_info["id"]),
        user_email=user_info["email"],
        user_name=user_info["login"],
    )


@oauth_before_login.connect
def before_login(blueprint: OAuth2ConsumerBlueprint, url: str) -> None:
    # pylint: disable=unused-argument
    flask.session["next_url"] = flask.request.args.get("next_url")


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/google", methods=["GET"])
def login_google() -> str:
    """
    ---
    get:
        summary: Authenticate user using Google.
        tags:
            - auth
        responses:
            302:
                description: Redirect the user to the index page upon successfull authentication.
    """
    if not google.authorized:
        return redirect(url_for("google.login"))
    res = google.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on Google"


@bp.route("/discord", methods=["GET"])
def login_discord() -> str:
    """
    ---
    get:
        summary: Authenticate user using Discord.
        tags:
            - auth
        responses:
            302:
                description: Redirect the user to the index page upon successfull authentication.
    """
    if not discord.authorized:
        return redirect(url_for("discord.login"))
    res = discord.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on Discord"


@bp.route("/reddit", methods=["GET"])
def login_reddit() -> str:
    """
    ---
    get:
        summary: Authenticate user using Reddit.
        tags:
            - auth
        responses:
            302:
                description: Redirect the user to the index page upon successfull authentication.
    """
    if not reddit.authorized:
        return redirect(url_for("reddit.login"))
    res = reddit.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on Reddit"


@bp.route("/twitch", methods=["GET"])
def login_twitch() -> str:
    """
    ---
    get:
        summary: Authenticate user using Twitch.
        tags:
            - auth
        responses:
            302:
                description: Redirect the user to the index page upon successfull authentication.
    """
    if not twitch.authorized:
        return redirect(url_for("twitch.login"))
    res = twitch.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on Twitch"


@bp.route("/logout")
@login_required
def logout() -> None:
    """
    ---
    get:
        summary: Logout authenticated user.
        tags:
            - auth
        responses:
            302:
                description: Redirect the user to the index page upon successfull logout.
            401:
                description: Unauthorized user.
    """
    logout_user()
    return redirect("/")


# because envoyExtAuthzHttp adds original requested resource path to the end, we need a wildcard pattern here
@bp.route("/verify", methods=["GET"], defaults={"path": ""})
@bp.route("/verify/<path:path>", methods=["GET"])
@login_required
def auth_verify(path: str) -> Response:  # pylint: disable=unused-argument
    """
    ---
    get:
        summary: Authenticate user (through the flask's "session" cookie) or app (e.g. sigsvc_authtoken)
        tags:
            - auth
        responses:
            200:
                description: Authenticated user/app.
            401:
                description: Unauthenticated user/app.
    """
    if "session" not in request.cookies:
        # app2app auth
        # TODO: work on a better and secure implementation
        # e.g. we must accept consumer ids and auth token should be signed with a temp signature
        sigsvc_auth_token = request.cookies.get("sigsvc_authtoken", None)
        if not sigsvc_auth_token or sigsvc_auth_token != SIGSVC_AUTH_TOKEN:
            return "", 401
        return "", 200
    elif not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    resp = flask.make_response()
    resp.headers[HTTP_HEADER_X_AUTH_UID] = str(current_user.id)
    return resp, 200
