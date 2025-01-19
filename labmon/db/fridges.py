import string
from typing import List
from sqlalchemy import (
    Sequence,
    Integer,
    Unicode,
    UnicodeText,
    Identity,
    ForeignKey,
    TIMESTAMP,
    Float,
    Table,
    Column,
    select
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.exc import NoResultFound

from . import Base, db
from .fridge_table import SensorReading

_fridge_classes: dict[str, SensorReading] = {}


class Fridge(Base):
    fridge_id: Mapped[int] = mapped_column(
        "id", Identity("fridge_id_seq"), primary_key=True
    )
    name: Mapped[str] = mapped_column(Unicode(255), unique=True)
    fridge_table_name: Mapped[str] = mapped_column(Unicode(255), unique=True)
    comment: Mapped[str] = mapped_column(UnicodeText)
    sensors: Mapped[List["Sensor"]] = relationship(back_populates="fridge")
    supplementary: Mapped[List["FridgeSupplementary"]] = relationship(
        back_populates="fridge"
    )
    __tablename__ = "fridges"

    def __init__(self, name, fridge_table_name=None, sensors=(), comment=""):
        self.name = name
        # Derive a table name if not given
        if fridge_table_name is None:
            fridge_table_name = self._sanitize_name(name)
        self.fridge_table_name = fridge_table_name
        for sensor in sensors:
            self.sensors.append(sensor)
        self.comment = comment

    @staticmethod
    def _sanitize_name(name):
        """
        Sanitize a name to a format acceptable for table names
        """
        return "".join(
            c.lower() if c in string.ascii_letters + string.digits else "_"
            for c in name
        )

    @classmethod
    def get_fridge_by_name(cls, name):
        """
        Return a fridge object from the given name
        """
        try:
            query = select(cls).where(cls.name == name)
            fridge = db.session.execute(query).scalar_one()
            return fridge
        except NoResultFound as exc:
            raise KeyError(f"Fridge {name} not found") from exc


    def fridge_table(self) -> SensorReading:
        # Check if we have an instance of the fridge table in cache
        if self.fridge_table_name in _fridge_classes:
            return _fridge_classes[self.fridge_table_name]
        # Otherwise we create an instance of the fridge table
        new_fridge_table = Table(
            self.fridge_table_name,
            Base.registry.metadata,
            Column("time", TIMESTAMP, primary_key=True),
            *(Column(sensor.column_name, Float) for sensor in self.sensors),
        )

        # Create a new class to represent the fridge
        fridge_class = type(self.fridge_table_name, (SensorReading,), {})

        # Map the class to the table
        Base.registry.map_imperatively(fridge_class, new_fridge_table)

        _fridge_classes[self.fridge_table_name] = fridge_class
        return fridge_class


class FridgeSupplementary(Base):
    supp_id: Mapped[int] = mapped_column(
        "id", Integer, Sequence("fridges_supplementary_id_seq"), primary_key=True
    )
    fridge_id: Mapped[int] = mapped_column(ForeignKey("fridges.id"))
    fridge: Mapped["Fridge"] = relationship(repr=False)
    supp_table_name: Mapped[str] = mapped_column(Unicode(1024))
    name: Mapped[str] = mapped_column(Unicode(1024))
    label: Mapped[str] = mapped_column(Unicode(1024))
    comment: Mapped[str] = mapped_column(UnicodeText())
    sensors: Mapped[List["SensorSupplementary"]] = relationship(
        back_populates="fridge_supp"
    )
    __tablename__ = "fridges_supplementary"

    def __init__(self, name, supp_table_name, label, sensors, comment=None):
        self.name = name
        self.supp_table_name = supp_table_name
        self.label = label
        for sensor in sensors:
            self.sensors.append(sensor)
        self.comment = comment

    def fridge_table(self):
        # Check if we have an instance of the fridge table in cache
        if self.supp_table_name in _fridge_classes:
            return _fridge_classes[self.supp_table_name]
        # Otherwise we create an instance of the fridge table
        new_supp_fridge_table = Table(
            self.fridge_table_name,
            Base.registry.metadata,
            Column("time", TIMESTAMP, primary_key=True),
            *(Column(sensor.column_name, Float) for sensor in self.sensors),
        )

        # Create a new class to represent the fridge
        supp_fridge_class = type(self.supp_table_name, (SensorReading,), {})

        # Map the class to the table
        Base.registry.map_imperatively(supp_fridge_class, new_supp_fridge_table)

        _fridge_classes[self.supp_table_name] = supp_fridge_class
        return supp_fridge_class
