import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase


def StrEnum(enum_cls: type[enum.Enum]) -> SAEnum:
    """Store str-enum values in PostgreSQL (e.g. 'documentary'), not member names ('DOCUMENTARY')."""
    return SAEnum(enum_cls, values_callable=lambda members: [m.value for m in members])


class Base(DeclarativeBase):
    pass
