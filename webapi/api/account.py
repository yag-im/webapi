from flask import (
    Blueprint,
    Response,
    request,
)

import webapi.biz.account as biz_account
from webapi.api.const import HTTP_HEADER_X_UID
from webapi.dto.account import (
    GetUserResponseDTO,
    UpdateUserRequestDTO,
)

bp = Blueprint("account", __name__, url_prefix="/api/accounts")


@bp.route("/user", methods=["GET"])
def get_user() -> Response:
    """
    ---
    get:
        summary: Get user info.
        tags:
            - account
        responses:
            200:
                content:
                    application/json:
                        schema: GetUserResponseDTO
    """
    user_id = request.headers.get(HTTP_HEADER_X_UID, None)
    if not user_id:
        return "", 401
    user = biz_account.get_user(int(user_id))
    return GetUserResponseDTO.Schema().dump(user)


@bp.route("/user", methods=["PUT"])
def update_user() -> Response:
    """
    ---
    put:
        summary: Update user info.
        tags:
            - account
        requestBody:
            required: true
            content:
                application/json:
                    schema: UpdateUserRequestDTO
        responses:
            200:
                description: User info was successfully updated.
            401:
                description: Unauthorized user.
    """
    user_id = request.headers.get(HTTP_HEADER_X_UID, None)
    if not user_id:
        return "", 401
    user = UpdateUserRequestDTO.Schema().load(data=request.get_json())
    biz_account.update_user(int(user_id), user)
    return "", 200
