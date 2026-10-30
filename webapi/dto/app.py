import typing as t

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from webapi.dto.account import MyStuffType
from webapi.dto.fields import ByName
from webapi.services.dto.appsvc import SearchAppsOrderBy


class SearchAppsRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: t.Optional[str] = Field(default=None, min_length=3)
    offset: int = 0
    limit: int = 100
    order_by: t.Optional[SearchAppsOrderBy] = SearchAppsOrderBy.TS_ADDED
    publisher_name: t.Optional[str] = None
    my_stuff: t.Optional[t.Annotated[MyStuffType, ByName()]] = None
    lang: t.Optional[str] = None
