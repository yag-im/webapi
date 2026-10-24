import logging
import os
import typing as t
from enum import StrEnum
from http import HTTPStatus

from authlib.integrations.starlette_client import (
    OAuth,
    OAuthError,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
)
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from webapi.api.const import HTTP_HEADER_X_AUTH_UID
from webapi.models.account import UserDAO
from webapi.models.auth import OAuthDAO
from webapi.sqldb import get_db

log = logging.getLogger("webapi")

SESSION_USER_ID = "user_id"
SESSION_NEXT_URL = "next_url"


class Provider(StrEnum):
    GOOGLE = "google"
    DISCORD = "discord"
    REDDIT = "reddit"
    TWITCH = "twitch"


class ProviderUser(t.NamedTuple):
    id: str
    email: t.Optional[str] = None
    name: t.Optional[str] = None


oauth = OAuth()
oauth.register(
    Provider.GOOGLE,
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",  # noqa: S106
    api_base_url="https://www.googleapis.com/",
    client_kwargs={"scope": "https://www.googleapis.com/auth/userinfo.email"},
)
oauth.register(
    Provider.DISCORD,
    client_id=os.getenv("DISCORD_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("DISCORD_OAUTH_CLIENT_SECRET"),
    authorize_url="https://discord.com/api/oauth2/authorize",
    authorize_params={"prompt": "consent"},
    access_token_url="https://discord.com/api/oauth2/token",  # noqa: S106
    api_base_url="https://discord.com/",
    client_kwargs={"scope": "identify email"},
)
oauth.register(
    Provider.REDDIT,
    client_id=os.getenv("REDDIT_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_OAUTH_CLIENT_SECRET"),
    authorize_url="https://www.reddit.com/api/v1/authorize",
    access_token_url="https://www.reddit.com/api/v1/access_token",  # noqa: S106
    api_base_url="https://oauth.reddit.com/",
    # reddit does not expose the user's email to 3rd parties; its API rejects generic user agents
    user_agent="yag-webapi",
    client_kwargs={"scope": "identity"},
)
oauth.register(
    Provider.TWITCH,
    client_id=os.getenv("TWITCH_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("TWITCH_OAUTH_CLIENT_SECRET"),
    authorize_url="https://id.twitch.tv/oauth2/authorize",
    access_token_url="https://id.twitch.tv/oauth2/token",  # noqa: S106
    api_base_url="https://api.twitch.tv/helix/",
    client_kwargs={
        "scope": "user:read:email",
        "token_endpoint_auth_method": "client_secret_post",
        "headers": {"Client-Id": os.getenv("TWITCH_OAUTH_CLIENT_ID", "")},
    },
)

# provider -> (user info endpoint, user info parser)
USER_INFO: dict[Provider, tuple[str, t.Callable[[t.Any], ProviderUser]]] = {
    Provider.GOOGLE: ("/oauth2/v3/userinfo", lambda u: ProviderUser(id=str(u["sub"]), email=u["email"])),
    Provider.DISCORD: (
        "/api/users/@me",
        lambda u: ProviderUser(id=str(u["id"]), email=u["email"], name=u["username"]),
    ),
    Provider.REDDIT: ("/api/v1/me", lambda u: ProviderUser(id=str(u["id"]), name=u["name"])),
    Provider.TWITCH: (
        "/helix/users",
        lambda u: ProviderUser(id=str(u["data"][0]["id"]), email=u["data"][0]["email"], name=u["data"][0]["login"]),
    ),
}

DbSession = t.Annotated[Session, Depends(get_db)]


def get_current_user(request: Request, db: DbSession) -> t.Optional[UserDAO]:
    user_id = request.session.get(SESSION_USER_ID)
    return db.get(UserDAO, user_id) if user_id is not None else None


CurrentUser = t.Annotated[t.Optional[UserDAO], Depends(get_current_user)]


def login_required(user: CurrentUser) -> UserDAO:
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
    return user


LoggedInUser = t.Annotated[UserDAO, Depends(login_required)]


def sign_in_user(db: Session, provider: Provider, token: dict, provider_user: ProviderUser) -> t.Optional[int]:
    """Returns id of the local user bound to the provider account (created if missing), or None if inactive."""
    oauth_rec = db.scalars(
        select(OAuthDAO).filter_by(provider=provider.value, provider_user_id=provider_user.id)
    ).one_or_none()
    if oauth_rec is None:
        oauth_rec = OAuthDAO(provider=provider.value, provider_user_id=provider_user.id, token=token)
    user = oauth_rec.user
    if user is None:
        # If this OAuth token doesn't have an associated local account,
        # create a new local user account for this user.
        # Remember that `email` can be None, e.g. if the user declines
        # to publish their email address on Google!
        user = UserDAO(email=provider_user.email, name=provider_user.name)
        oauth_rec.user = user
        db.add(oauth_rec)
        db.commit()
    return user.id if user.is_active else None


bp = APIRouter(prefix="/auth", tags=["auth"])


@bp.get(
    "/logout",
    summary="Logout authenticated user.",
    status_code=HTTPStatus.FOUND,
    response_description="Redirect the user to the index page upon successful logout.",
    responses={401: {"description": "Unauthorized user."}},
    dependencies=[Depends(login_required)],
)
def logout(request: Request) -> RedirectResponse:
    request.session.pop(SESSION_USER_ID, None)
    return RedirectResponse("/", status_code=HTTPStatus.FOUND)


# because envoyExtAuthzHttp adds original requested resource path to the end, we need a wildcard pattern here
# also envoyExtAuthzHttp sends original HTTP method lol
@bp.get(
    "/verify",
    summary='Authenticate user (through the "session" cookie).',
    response_description="Authenticated user.",
    responses={401: {"description": "Unauthenticated user."}},
)
@bp.api_route("/verify", methods=["POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
@bp.api_route("/verify/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
def auth_verify(user: LoggedInUser) -> Response:
    return Response(headers={HTTP_HEADER_X_AUTH_UID: str(user.id)})


@bp.get(
    "/{provider}",
    summary="Authenticate user using an OAuth provider.",
    status_code=HTTPStatus.FOUND,
    response_description="Redirect the user to the provider's login page.",
)
@bp.get("/login/{provider}", include_in_schema=False)
async def login(request: Request, provider: Provider, next_url: t.Optional[str] = None) -> Response:
    request.session[SESSION_NEXT_URL] = next_url
    redirect_uri = request.url_for("oauth_authorized", provider=provider.value)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@bp.get("/login/{provider}/authorized", include_in_schema=False, name="oauth_authorized")
async def oauth_authorized(request: Request, provider: Provider, db: DbSession) -> RedirectResponse:
    next_url = request.session.pop(SESSION_NEXT_URL, None) or "/"
    client = oauth.create_client(provider)
    try:
        token = await client.authorize_access_token(request)
    except OAuthError as e:
        log.warning("failed to log in with %s: %s", provider, e)
        return RedirectResponse("/", status_code=HTTPStatus.FOUND)

    user_info_url, parse_user_info = USER_INFO[provider]
    resp = await client.get(user_info_url, token=token)
    if resp.is_error:
        log.error("failed to fetch user info from %s", provider)
        return RedirectResponse("/", status_code=HTTPStatus.FOUND)
    provider_user = parse_user_info(resp.json())

    user_id = await run_in_threadpool(sign_in_user, db, provider, dict(token), provider_user)
    if user_id is not None:
        request.session[SESSION_USER_ID] = user_id
        log.debug("successfully signed in with %s.", provider)
    else:
        log.warning("user %s can't be signed in (is user active?).", provider_user.name)
    return RedirectResponse(next_url, status_code=HTTPStatus.FOUND)
