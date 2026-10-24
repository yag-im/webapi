import typing as t
from http import HTTPStatus

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Response,
)

from webapi.api.const import HTTP_HEADER_X_AUTH_UID
from webapi.dto.account import (
    GetUserResponseDTO,
    PatchUserRequestDTO,
    UpdateUserRequestDTO,
)
from webapi.services import accountsvc

bp = APIRouter(prefix="/api/accounts", tags=["account"])

# set by the gateway after a successful /auth/verify
AuthUid = t.Annotated[t.Optional[str], Header(alias=HTTP_HEADER_X_AUTH_UID)]

UNAUTHORIZED_RESPONSE: dict[int | str, dict[str, t.Any]] = {401: {"description": "Unauthorized user."}}


def _require_uid(uid: t.Optional[str]) -> int:
    if not uid:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
    return int(uid)


@bp.get("/user", summary="Get user info.", responses=UNAUTHORIZED_RESPONSE)
def get_user(x_auth_uid: AuthUid = None) -> GetUserResponseDTO:
    return accountsvc.get_user(_require_uid(x_auth_uid))


@bp.put(
    "/user",
    summary="Update user info.",
    response_description="User info was successfully updated.",
    responses=UNAUTHORIZED_RESPONSE,
)
def update_user(user: UpdateUserRequestDTO, x_auth_uid: AuthUid = None) -> Response:
    accountsvc.update_user(_require_uid(x_auth_uid), user)
    return Response(status_code=HTTPStatus.OK)


@bp.patch(
    "/user",
    summary="Partially update user info.",
    response_description="User info was successfully updated.",
    responses=UNAUTHORIZED_RESPONSE,
)
def patch_user(user: t.Optional[PatchUserRequestDTO] = None, x_auth_uid: AuthUid = None) -> Response:
    accountsvc.patch_user(_require_uid(x_auth_uid), user or PatchUserRequestDTO())
    return Response(status_code=HTTPStatus.OK)
