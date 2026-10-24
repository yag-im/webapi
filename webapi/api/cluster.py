from fastapi import APIRouter

import webapi.biz.cluster as biz_cluster
from webapi.services.dto.cluster_status import ClusterStatusResponseDTO

bp = APIRouter(tags=["cluster_status"])


@bp.get("/api/status", summary="Get cluster status by region.")
def status() -> ClusterStatusResponseDTO:
    return biz_cluster.cluster_status()
