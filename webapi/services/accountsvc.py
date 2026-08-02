import json
import os

from webapi.biz.errors import AccountSvcException
from webapi.dto.account import (
    GetUserResponseDTO,
    PatchUserRequestDTO,
    UpdateUserRequestDTO,
)
from webapi.services.helpers import get_requests_session

REQUESTS_TIMEOUT_CONN_READ = (3, 10)
ACCOUNTSVC_URL = os.environ["ACCOUNTSVC_URL"]


def get_user(user_id: int) -> GetUserResponseDTO:
    s = get_requests_session()
    res = s.get(
        url=f"{ACCOUNTSVC_URL}/users/{user_id}",
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AccountSvcException(res.text)
    return GetUserResponseDTO.Schema().load(res.json())


def update_user(user_id: int, user: UpdateUserRequestDTO) -> None:
    s = get_requests_session()
    res = s.put(
        url=f"{ACCOUNTSVC_URL}/users/{user_id}",
        data=json.dumps(UpdateUserRequestDTO.Schema().dump(user)),
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AccountSvcException(res.text)


def patch_user(user_id: int, user: PatchUserRequestDTO, fields: set) -> None:
    s = get_requests_session()
    payload = {k: v for k, v in PatchUserRequestDTO.Schema().dump(user).items() if k in fields}
    res = s.patch(
        url=f"{ACCOUNTSVC_URL}/users/{user_id}",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AccountSvcException(res.text)
