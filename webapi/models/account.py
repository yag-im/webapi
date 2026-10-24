import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    String,
)
from sqlalchemy.dialects.postgresql import (
    DATE,
    JSONB,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from webapi.sqldb import Base


class UserDAO(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "accounts"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str | None] = mapped_column(String(256))
    name: Mapped[str | None] = mapped_column(String(256))
    tz: Mapped[str] = mapped_column(String, server_default="UTC")
    apps_lib: Mapped[dict | None] = mapped_column(JSONB)
    dob: Mapped[datetime.date] = mapped_column(DATE, server_default="1970-01-01")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="TRUE")
