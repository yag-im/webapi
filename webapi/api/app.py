from fastapi import APIRouter

import webapi.biz.app as biz_app
from webapi.api.auth import CurrentUser
from webapi.dto.app import SearchAppsRequestDTO
from webapi.services.dto.appsvc import (
    GetAppReleaseResponseDTO,
    SearchAppsAclRequestDTO,
    SearchAppsAclResponseDTO,
    SearchAppsResponseDTO,
)

bp = APIRouter(prefix="/api/apps", tags=["application"])


@bp.get("/{app_release_uuid}", summary="Get application release details.")
def get_app_release(app_release_uuid: str) -> GetAppReleaseResponseDTO:
    return biz_app.get_app_release(app_release_uuid)


@bp.post("/search", summary="Search applications.")
def search_apps(req: SearchAppsRequestDTO, user: CurrentUser) -> SearchAppsResponseDTO:
    return biz_app.search_apps(req, user.id if user else None)


@bp.post("/search/acl", summary="Search helper: auto-complete list.")
def search_apps_acl(req: SearchAppsAclRequestDTO) -> SearchAppsAclResponseDTO:
    return biz_app.search_apps_acl(req)
