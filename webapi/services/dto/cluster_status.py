from pydantic import BaseModel


class ClusterStatusResponseDTO(BaseModel):
    class RegionUsage(BaseModel):
        region: str
        usage: float

    regions: list[RegionUsage]
