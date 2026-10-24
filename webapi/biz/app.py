import typing as t

from webapi.dto.app import SearchAppsRequestDTO
from webapi.services import appsvc
from webapi.services.dto.appsvc import (
    GetAppReleaseResponseDTO,
    SearchAppsAclRequestDTO,
    SearchAppsAclResponseDTO,
    SearchAppsRequestOutDTO,
    SearchAppsResponseDTO,
)


def get_app_release(app_release_uuid: str) -> GetAppReleaseResponseDTO:
    return appsvc.get_app_release(app_release_uuid)


def search_apps(req: SearchAppsRequestDTO, user_id: t.Optional[int]) -> SearchAppsResponseDTO:
    return appsvc.search_apps(
        SearchAppsRequestOutDTO(
            app_name=req.app_name,
            publisher_name=req.publisher_name,
            lang=req.lang,
            my_stuff=req.my_stuff,
            user_id=user_id,
            offset=req.offset,
            limit=req.limit,
            order_by=req.order_by,
        )
    )


def search_apps_acl(req: SearchAppsAclRequestDTO) -> SearchAppsAclResponseDTO:
    return appsvc.search_apps_acl(req)
