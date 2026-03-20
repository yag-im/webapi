import os

from webapi.biz.errors import JukeboxSvcException
from webapi.services.dto.cluster_status import ClusterStatusResponseDTO
from webapi.services.helpers import get_requests_session

REQUESTS_TIMEOUT_CONN_READ = (3, 10)
JUKEBOXSVC_URL = os.environ["JUKEBOXSVC_URL"]


def get_cluster_status() -> ClusterStatusResponseDTO:
    s = get_requests_session()
    res = s.get(
        url=f"{JUKEBOXSVC_URL}/cluster/status",
        headers={"Content-Type": "application/json"},
        timeout=REQUESTS_TIMEOUT_CONN_READ,
    )
    if res.status_code != 200:
        raise JukeboxSvcException(res.text)
    return ClusterStatusResponseDTO.Schema().load(res.json())
