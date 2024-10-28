import typing as t
from dataclasses import field

from marshmallow import (
    Schema,
    validate,
)
from marshmallow_dataclass import dataclass

from yagsvc.services.dto.appsvc import SearchAppsOrderBy


@dataclass
class SearchAppsRequestDTO:
    app_name: t.Optional[str] = field(default=None, metadata={"validate": validate.Length(min=2)})
    offset: int = 0
    limit: int = 100
    order_by: t.Optional[SearchAppsOrderBy] = field(default=SearchAppsOrderBy.TS_ADDED, metadata={"by_value": True})
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name
