import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from webapi.models.account import UserDAO
from webapi.sqldb import Base


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


class OAuthDAO(Base):
    # table layout inherited from Flask-Dance's OAuthConsumerMixin
    __tablename__ = "flask_dance_oauth"
    __table_args__ = {"schema": "accounts"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)
    token: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON))
    provider_user_id: Mapped[str | None] = mapped_column(String(256), unique=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(UserDAO.id))
    user: Mapped[UserDAO | None] = relationship(UserDAO)
