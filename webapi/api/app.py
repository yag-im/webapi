from flask import (
    Blueprint,
    Response,
    request,
)

import webapi.biz.app as biz_app
from webapi.dto.app import SearchAppsRequestDTO
from webapi.services.dto.appsvc import (
    GetAppReleaseResponseDTO,
    SearchAppsAclRequestDTO,
    SearchAppsAclResponseDTO,
    SearchAppsResponseDTO,
)

bp = Blueprint("app", __name__, url_prefix="/api/apps")


@bp.route("/<app_release_uuid>", methods=["GET"])
def get_app_release(app_release_uuid: str) -> Response:
    """
    ---
    get:
        summary: Get application release details.
        tags:
            - application
        parameters:
            - in: path
              type: integer
              name: app_release_uuid
              description: App release UUID
        responses:
            200:
                content:
                    application/json:
                        schema: GetAppReleaseResponseDTO
    """
    return GetAppReleaseResponseDTO.Schema().dump(biz_app.get_app_release(app_release_uuid))


@bp.route("/search", methods=["POST"])
def search_apps() -> Response:
    """
    ---
    post:
        summary: Search applications.
        tags:
            - application
        requestBody:
            required: true
            content:
                application/json:
                    schema: SearchAppsRequestDTO
        responses:
            200:
                content:
                    application/json:
                        schema: SearchAppsResponseDTO
    """
    req: SearchAppsRequestDTO = SearchAppsRequestDTO.Schema().load(data=request.get_json())
    return SearchAppsResponseDTO.Schema().dump(biz_app.search_apps(req))


@bp.route("/search/acl", methods=["POST"])
def search_apps_acl() -> Response:
    """
    ---
    post:
        summary: "Search helper: auto-complete list."
        tags:
            - application
        requestBody:
            required: true
            content:
                application/json:
                    schema: SearchAppsAclRequestDTO
        responses:
            200:
                content:
                    application/json:
                        schema: SearchAppsAclResponseDTO
    """
    req: SearchAppsAclRequestDTO = SearchAppsAclRequestDTO.Schema().load(data=request.get_json())
    return SearchAppsAclResponseDTO.Schema().dump(biz_app.search_apps_acl(req))
