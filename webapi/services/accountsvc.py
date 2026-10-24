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
    return GetUserResponseDTO.model_validate(res.json())


def update_user(user_id: int, user: UpdateUserRequestDTO) -> None:
    s = get_requests_session()
    res = s.put(
        url=f"{ACCOUNTSVC_URL}/users/{user_id}",
        data=user.model_dump_json(),
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AccountSvcException(res.text)


def patch_user(user_id: int, user: PatchUserRequestDTO) -> None:
    s = get_requests_session()
    res = s.patch(
        url=f"{ACCOUNTSVC_URL}/users/{user_id}",
        data=user.model_dump_json(exclude_unset=True),
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise AccountSvcException(res.text)
