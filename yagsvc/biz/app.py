import datetime

from dateutil.relativedelta import relativedelta
from flask_login import (
    AnonymousUserMixin,
    current_user,
)

from yagsvc.dto.app import SearchAppsRequestDTO
from yagsvc.services import appsvc
from yagsvc.services.dto.appsvc import (
    GetAppReleaseResponseDTO,
    SearchAppsAclRequestDTO,
    SearchAppsAclResponseDTO,
    SearchAppsRequestOutDTO,
    SearchAppsResponseDTO,
)


def get_app_release(app_release_uuid: str) -> GetAppReleaseResponseDTO:
    return appsvc.get_app_release(app_release_uuid)


def search_apps(req: SearchAppsRequestDTO) -> SearchAppsResponseDTO:
    now_date = datetime.datetime.now().date()
    kids_mode = False
    if not isinstance(current_user, AnonymousUserMixin):
        kids_mode = relativedelta(now_date, current_user.dob).years < 10

    return appsvc.search_apps(
        SearchAppsRequestOutDTO(
            app_name=req.app_name,
            kids_mode=kids_mode,
            offset=req.offset,
            limit=req.limit,
            order_by=req.order_by,
        )
    )


def search_apps_acl(req: SearchAppsAclRequestDTO) -> SearchAppsAclResponseDTO:
    return appsvc.search_apps_acl(req)
