import typing as t

from marshmallow import Schema
from marshmallow_dataclass import dataclass


@dataclass
class ClusterStatusResponseDTO:
    @dataclass
    class RegionUsage:
        region: str
        usage: float

    regions: list[RegionUsage]
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name
