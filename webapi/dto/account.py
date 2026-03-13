import datetime
import typing as t
from enum import StrEnum

from marshmallow import Schema
from marshmallow_dataclass import dataclass


class AgeMode(StrEnum):
    KID = "K"
    TEEN = "T"
    ADULT = "A"


DEFAULT_AGE_MODE = AgeMode.TEEN


@dataclass
class UserDC:
    email: t.Optional[str]
    name: t.Optional[str]
    tz: str
    apps_lib: t.Optional[dict]
    dob: datetime.date


@dataclass
class GetUserResponseDTO(UserDC):
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class UpdateUserRequestDTO(UserDC):
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name
