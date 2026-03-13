import datetime

from dateutil.relativedelta import relativedelta
from flask import current_app as app
from flask_login import (
    AnonymousUserMixin,
    current_user,
)

from webapi.dto.account import (
    DEFAULT_AGE_MODE,
    AgeMode,
)
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


def search_apps(req: SearchAppsRequestDTO) -> SearchAppsResponseDTO:
    now_date = datetime.datetime.now().date()
    age_mode = DEFAULT_AGE_MODE
    if not isinstance(current_user, AnonymousUserMixin):
        age = relativedelta(now_date, current_user.dob).years
        if age < 13:
            age_mode = AgeMode.KID
        elif age < 18:
            age_mode = AgeMode.TEEN
        else:
            age_mode = AgeMode.ADULT
        app.logger.error(
            f"user id: {current_user.id} user dob: {current_user.dob} user age: {age}, age_mode: {age_mode}"
        )

    return appsvc.search_apps(
        SearchAppsRequestOutDTO(
            app_name=req.app_name,
            publisher_name=req.publisher_name,
            age_mode=age_mode,
            offset=req.offset,
            limit=req.limit,
            order_by=req.order_by,
        )
    )


def search_apps_acl(req: SearchAppsAclRequestDTO) -> SearchAppsAclResponseDTO:
    return appsvc.search_apps_acl(req)
