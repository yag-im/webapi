from webapi.services import jukeboxsvc
from webapi.services.dto.cluster_status import ClusterStatusResponseDTO


def cluster_status() -> ClusterStatusResponseDTO:
    return jukeboxsvc.get_cluster_status()
