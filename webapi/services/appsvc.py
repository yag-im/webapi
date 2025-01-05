import json
import os

from webapi.biz.errors import AppSvcException
from webapi.services.dto.appsvc import (
    GetAppReleaseResponseDTO,
    SearchAppsAclRequestDTO,
    SearchAppsAclResponseDTO,
    SearchAppsRequestOutDTO,
    SearchAppsResponseDTO,
)
from webapi.services.helpers import get_requests_session

REQUESTS_TIMEOUT_CONN_READ = (3, 10)
APPSVC_URL = os.environ["APPSVC_URL"]


def search_apps_acl(req: SearchAppsAclRequestDTO) -> SearchAppsAclResponseDTO:
    s = get_requests_session()
    res = s.post(
        url=f"{APPSVC_URL}/apps/search/acl",
        data=json.dumps(SearchAppsAclRequestDTO.Schema().dump(req)),
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AppSvcException(res.text)
    return res.json()


def search_apps(req: SearchAppsRequestOutDTO) -> SearchAppsResponseDTO:
    s = get_requests_session()
    res = s.post(
        url=f"{APPSVC_URL}/apps/search",
        data=json.dumps(SearchAppsRequestOutDTO.Schema().dump(req)),
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AppSvcException(res.text)
    return res.json()


def get_app_release(app_release_uuid: str) -> GetAppReleaseResponseDTO:
    s = get_requests_session()
    res = s.get(
        url=f"{APPSVC_URL}/apps/{app_release_uuid}",
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AppSvcException(res.text)
    return res.json()
