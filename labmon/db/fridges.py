import string
from typing import List
from sqlalchemy import Sequence, Integer, Unicode, UnicodeText, Identity, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, db
from .fridge_table import FridgeTable

class Fridge(Base):
    fridge_id: Mapped[int] = mapped_column("id", Identity("fridge_id_seq"), primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(255), unique=True)
    comment: Mapped[str] = mapped_column(UnicodeText)
    sensors: Mapped[List["Sensor"]] = relationship(back_populates='fridge')
    supplementary: Mapped[List["FridgeSupplementary"]] = relationship(back_populates='fridge')
    __tablename__ = "fridges"

class Bla:
    # Cache of existing table definitions
    __tables__ = {}

    def __init__(self, name, sensors, comment=None):
        self.name = name
        for sensor in sensors:
            self.sensors.append(Sensors.get_sensor(sensor, self, True))
        self.comment = comment if comment is not None else ""
        self._fridge_table = None

    def __repr__(self):
        return f"<Fridge {self.name}>"

    def get_sensor(self, sensor):
        return Sensors.get_sensor(sensor, self, False)

    def fridge_table(self):
        # Sanitize name by replacing all spacial characters
        name = "".join(c if c in string.ascii_letters+string.digits else "_" for c in self.name)
        if name in db.metadata.tables:
            return db.metadata.tables[name]
        elif not hasattr(self, '_fridge_table') or self._fridge_table is None:
            self._fridge_table = db.Table(name, db.metadata,
                                   db.Column('Time', db.TIMESTAMP, primary_key=True),
                                   *[db.Column(sensor.column_name, db.Float) for sensor in self.sensors])
        return self._fridge_table

    @classmethod
    def get_fridge(cls, name):
        # Sanitize name by replacing all spacial characters
        name = "".join(c if c in string.ascii_letters+string.digits else " " for c in name)
        res = Fridge.query.filter(Fridge.name==name).first()
        if res is None:
            raise KeyError("Unable to find fridge")
        return res


class FridgeSupplementary(Base):
    supp_id: Mapped[int] = mapped_column("id", Integer, Sequence("fridges_supplementary_id_seq"), primary_key=True)
    fridge_id: Mapped[int] = mapped_column(ForeignKey("fridges.id"))
    fridge: Mapped["Fridge"] = relationship(repr=False)
    table_name: Mapped[str] = mapped_column(Unicode(1024))
    name: Mapped[str] = mapped_column(Unicode(1024))
    label: Mapped[str] = mapped_column(Unicode(1024))
    comment: Mapped[str] = mapped_column(UnicodeText())
    sensors: Mapped[List["SensorSupplementary"]] = relationship(back_populates='fridge_supp')
    __tablename__ = "fridges_supplementary"

class bla2:
    def __init__(self, name, table_name, label, sensors, comment=None):
        self.table_name = table_name
        self.name = name
        self.label = label
        for sensor in sensors:
            self.sensors.append(SensorsSupplementary.get_sensor(sensor, self, True))
        self.comment = comment

    def get_sensor(self, sensor):
        return SensorsSupplementary.get_sensor(sensor, self, False)

    def __repr__(self):
        return f"<Supplementary for {self.fridge}: {self.table_name}>"

    def fridge_table(self):
        # Sanitize name by replacing all spacial characters
        if self.table_name in db.metadata.tables:
            return db.metadata.tables[self.table_name]
        if self._suppl_table is None:
            self._suppl_table = db.Table(self.table_name, db.metadata,
                                         db.Column('Time', db.TIMESTAMP, primary_key=True),
                                         *[db.Column(sensor.column_name, db.Float) for sensor in self.sensors])
            return self._suppl_table
