from typing import List, Type, TypeVar
from sqlalchemy import (
    Integer,
    Unicode,
    UnicodeText,
)
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from .db import Base
from .fridge_table import SensorReading

SensorReadingT = TypeVar('SensorReadingT', bound=SensorReading)

class FridgeModel(Base):
    __abstract__ = True
    name: Mapped[str] = mapped_column(Unicode(255), unique=True)
    comment: Mapped[str] = mapped_column(UnicodeText)

    @declared_attr
    def sensors(cls) -> List["SensorModel"]:
        raise NotImplementedError("Not implemented in ABC")

    @classmethod
    def get_by_table_name(cls, name) -> "FridgeModel":
        raise NotImplementedError("Not implemented in ABC")

    def fridge_table(self) -> Type[SensorReadingT]:
        raise NotImplementedError("Not implemented in ABC")


class SensorModel(Base):
    __abstract__ = True
    display_name: Mapped[str] = mapped_column("name", Unicode(1024))
    column_name: Mapped[str] = mapped_column(Unicode(1024))
    view_order: Mapped[int] = mapped_column()
    visible: Mapped[bool] = mapped_column(Integer())

    @classmethod
    def get_sensor(cls, column_name, fridge) -> "SensorModel":
        raise NotImplementedError("Not implemented in ABC")
