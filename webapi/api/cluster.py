from flask import (
    Blueprint,
    Response,
)

import webapi.biz.cluster as biz_cluster
from webapi.services.dto.cluster_status import ClusterStatusResponseDTO

bp = Blueprint("cluster", __name__)


@bp.route("/api/status", methods=["GET"])
def status() -> Response:
    """
    ---
    get:
        summary: Get cluster status by region.
        tags:
            - cluster_status
        responses:
            200:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/ClusterStatusResponseDTO'
    """
    return ClusterStatusResponseDTO.Schema().dump(biz_cluster.cluster_status())
