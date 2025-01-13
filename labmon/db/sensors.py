from sqlalchemy import ForeignKey, Integer, Unicode, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, db


class Sensor(Base):
    """
    List of sensors attached to the fridge given by fridge_id
    """
    sensor_id: Mapped[int] = mapped_column("id", Identity("sensors_id_seq"), primary_key=True)
    fridge_id: Mapped[int] = mapped_column(ForeignKey("fridges.id"))
    fridge: Mapped["Fridge"] = relationship(back_populates="sensors", repr=None)
    column_name: Mapped[str] = mapped_column(Unicode(1024))
    display_name: Mapped[str] = mapped_column("name", Unicode(1024))
    view_order: Mapped[int] = mapped_column()
    visible: Mapped[bool] = mapped_column(Integer())
    __tablename__ = "sensors"

class bla3:
    def __init__(self, display_name, column_name, fridge, view_order=1, visible=1):
        if isinstance(fridge, Fridges):
            self.fridge_id = fridge.id
        else:
            self.fridge_id = int(fridge)
        self.display_name = display_name
        self.column_name = column_name
        self.view_order = view_order
        self.visible = visible

        db.Column.__init__(self, column_name, db.Float)

    def __repr__(self):
        return f"<Sensor {self.column_name}>"

    @classmethod
    def get_sensor(cls, name, fridge, add=False):
        if isinstance(fridge, Fridges):
            fridge_id = fridge.id
        else:
            fridge_id = int(fridge)

        sensor = cls.query.filter_by(column_name=name, fridge_id=fridge_id)
        if sensor.count() == 0 and add:
            safe_name = name.replace(' ', '_')
            sensor = Sensors(name, safe_name, fridge)
            db.session.add(sensor)
            return sensor
        elif sensor.count() == 0 and not add:
            raise KeyError("Sensor not found")
        return sensor.first()

class SensorSupplementary(Base):
    """
    List of sensors attached to the supplementary sensor set
    """
    sensor_id: Mapped[int] = mapped_column("id", Identity("sensors_supplementary_id_seq"), primary_key=True)
    fridge_suppl_id: Mapped[int] = mapped_column(ForeignKey("fridges_supplementary.id"))
    fridge_supp: Mapped["FridgeSupplementary"] = relationship(repr=False)
    column_name: Mapped[str] = mapped_column(Unicode(1024))
    display_name: Mapped[str] = mapped_column("name", Unicode(1024))
    view_order: Mapped[int] = mapped_column()
    visible: Mapped[bool] = mapped_column(Integer())
    __tablename__ = "sensors_supplementary"

class bla4:
    def __init__(self, name, fridge_suppl, column_name=None, view_order=1, visible=1):
        if isinstance(fridge_suppl, FridgesSupplementary):
            self.fridge_suppl_id = fridge_suppl.id
        else:
            self.fridge_suppl_id = int(fridge_suppl)
        self.column_name = name
        if column_name:
            self.column_name = column_name
        else:
            self.column_name = name
        self.view_order = view_order
        self.visible = visible

    def __repr__(self):
        return f"<Supplementary_Sensor {self.column_name}>"

    @classmethod
    def get_sensor(cls, name, fridge, add=False):
        if isinstance(fridge, FridgesSupplementary):
            suppl_id = fridge.id
        else:
            suppl_id = int(fridge)

        sensor = cls.query.filter_by(column_name=name, fridge_suppl_id=suppl_id)
        if sensor.count() == 0 and add:
            sensor = SensorsSupplementary(name, fridge, name)
            db.session.add(sensor)
            return sensor
        elif sensor.count() == 0 and not add:
            raise KeyError("Unknown Sensor")
        return sensor.first()
