import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase


def StrEnum(enum_cls: type[enum.Enum]) -> SAEnum:
    """Store str-enum values as VARCHAR (matches Alembic string columns)."""
    return SAEnum(
        enum_cls,
        values_callable=lambda members: [m.value for m in members],
        native_enum=False,
    )


class Base(DeclarativeBase):
    pass
