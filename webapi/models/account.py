from flask_login import UserMixin
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    String,
)
from sqlalchemy.dialects.postgresql import (
    DATE,
    JSONB,
)

from webapi.sqldb import sqldb


class UserDAO(UserMixin, sqldb.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "accounts"}
    id = Column(BigInteger, primary_key=True)
    email = Column(String(256), unique=False)
    name = Column(String(256), unique=False)
    tz = Column(String, nullable=False, server_default="UTC")
    apps_lib = Column(JSONB)
    dob = Column(DATE, nullable=False, server_default="1970-01-01")
    is_active = Column(Boolean, nullable=False, server_default="TRUE")
