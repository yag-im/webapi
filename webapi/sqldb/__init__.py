import typing as t

from sqlalchemy import (
    URL,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker()


def init_db(url: URL, engine_options: dict[str, t.Any]) -> None:
    SessionLocal.configure(bind=create_engine(url, **engine_options))


def get_db() -> t.Iterator[Session]:
    with SessionLocal() as session:
        yield session
