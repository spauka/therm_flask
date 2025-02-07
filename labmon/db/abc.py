from time import sleep
from typing import List, Type, TypeVar

from sqlalchemy import TIMESTAMP, Column, Float, Integer, Unicode, UnicodeText, inspect
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from .db import Base, db
from .fridge_table import SensorReading

SensorReadingT = TypeVar("SensorReadingT", bound=SensorReading)

# Cache of created fridge classes
_fridge_classes: dict[str, Type[SensorReadingT]] = {}


class FridgeModel(Base):
    __abstract__ = True
    name: Mapped[str] = mapped_column(Unicode(255), unique=True)
    table_name: Mapped[str] = mapped_column(Unicode(255), unique=True)
    label: Mapped[str] = mapped_column(Unicode(255))
    comment: Mapped[str] = mapped_column(UnicodeText)

    @declared_attr
    def sensors(cls) -> List["SensorModel"]:  # pylint: disable=no-self-argument
        raise NotImplementedError("Not implemented in ABC")

    def fridge_table(self, check_exists=True) -> Type[SensorReadingT]:
        """
        Return a reference to the table associated with a fridge or
        supplementary fridge dataset
        """
        # Check if we have an instance of the fridge table in cache
        if self.table_name in _fridge_classes:
            return _fridge_classes[self.table_name]

        # double check that the table exists. We can ignore this check if
        # we are ignoring this for the purpose of creating the table.
        if check_exists:
            inspector = inspect(db.engine)
            exists = inspector.has_table(self.table_name)
            if not exists:
                raise KeyError(
                    (
                        f"Could not find fridge table {self.table_name} in the database "
                        "even though it exists in the fridges table."
                    )
                )

        # Otherwise we create an instance of the fridge table
        # We have to fill in the annotations such that SQLAlchemy knows
        # to map the columns to the dataclass
        new_fridge_table = {
            "__tablename__": self.table_name,
            "__annotations__": {"time": Column},
            "time": mapped_column(TIMESTAMP(timezone=True), primary_key=True),
        }
        for sensor in self.sensors:
            new_fridge_table["__annotations__"][sensor.column_name] = Column
            new_fridge_table[sensor.column_name] = mapped_column(Float, nullable=True)
        try:
            fridge_class = type(
                self.table_name, (Base, SensorReading), new_fridge_table
            )
        except InvalidRequestError as e:
            # The table was created by another thread while we were working. Let's return
            # the existing table instead
            for _ in range(5):
                sleep(0.01)
                if self.table_name in _fridge_classes:
                    return _fridge_classes[self.table_name]
            raise RuntimeError(
                f"Couldn't create fridge class for {self.table_name}"
            ) from e

        _fridge_classes[self.table_name] = fridge_class
        return fridge_class


class SensorModel(Base):
    __abstract__ = True
    display_name: Mapped[str] = mapped_column("name", Unicode(1024))
    column_name: Mapped[str] = mapped_column(Unicode(1024))
    view_order: Mapped[int] = mapped_column()
    visible: Mapped[bool] = mapped_column(Integer())

    @classmethod
    def get_sensor(cls, column_name: str, fridge: FridgeModel) -> "SensorModel":
        raise NotImplementedError("Not implemented in ABC")
