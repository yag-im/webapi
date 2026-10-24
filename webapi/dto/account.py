import datetime
import typing as t
from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
)


class AgeMode(StrEnum):
    KID = "K"
    TEEN = "T"
    ADULT = "A"


DEFAULT_AGE_MODE = AgeMode.TEEN


class MyStuffType(StrEnum):
    FAVORITES = "favorites"
    RECENTLY_PLAYED = "recently_played"


class UserDC(BaseModel):
    id: t.Optional[int] = None
    email: t.Optional[str] = None
    name: t.Optional[str] = None
    tz: str
    apps_lib: t.Optional[dict] = None
    dob: datetime.date
    is_active: bool


class GetUserResponseDTO(UserDC):
    pass


class UpdateUserRequestDTO(UserDC):
    model_config = ConfigDict(extra="forbid")


class PatchUserRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: t.Optional[str] = None
    name: t.Optional[str] = None
    tz: t.Optional[str] = None
    apps_lib: t.Optional[dict] = None
    dob: t.Optional[datetime.date] = None
