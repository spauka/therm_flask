from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Unicode, Identity, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db
from .abc import SensorModel
if TYPE_CHECKING:
    from .fridges import Fridge, FridgeSupplementary


class Sensor(SensorModel):
    """
    List of sensors attached to the fridge given by fridge_id
    """

    sensor_id: Mapped[int] = mapped_column(
        "id", Identity("sensors_id_seq"), primary_key=True
    )
    fridge_id: Mapped[int] = mapped_column(ForeignKey("fridges.id"))
    fridge: Mapped["Fridge"] = relationship(back_populates="sensors", repr=False)
    display_name: Mapped[str] = mapped_column("name", Unicode(1024))
    column_name: Mapped[str] = mapped_column(Unicode(1024))
    view_order: Mapped[int] = mapped_column()
    visible: Mapped[bool] = mapped_column(Integer())
    __tablename__ = "sensors"

    def __init__(self, fridge, display_name, column_name, view_order=1, visible=1):
        self.fridge = fridge
        self.display_name = display_name
        self.column_name = column_name
        self.view_order = view_order
        self.visible = visible

    @classmethod
    def get_sensor(cls, column_name, fridge):
        query = select(cls).where(
            cls.fridge == fridge and cls.column_name == column_name
        )
        sensor = db.session.execute(query).scalar_one()
        return sensor


class SensorSupplementary(SensorModel):
    """
    List of sensors attached to the supplementary sensor set
    """

    sensor_id: Mapped[int] = mapped_column(
        "id", Identity("sensors_supplementary_id_seq"), primary_key=True
    )
    fridge_suppl_id: Mapped[int] = mapped_column(ForeignKey("fridges_supplementary.id"))
    fridge_supp: Mapped["FridgeSupplementary"] = relationship(repr=False)
    display_name: Mapped[str] = mapped_column("name", Unicode(1024))
    column_name: Mapped[str] = mapped_column(Unicode(1024))
    view_order: Mapped[int] = mapped_column()
    visible: Mapped[bool] = mapped_column(Integer())
    __tablename__ = "sensors_supplementary"

    def __init__(self, fridge_supp, display_name, column_name, view_order=1, visible=1):
        self.fridge_supp = fridge_supp
        self.display_name = display_name
        self.column_name = column_name
        self.view_order = view_order
        self.visible = visible

    @classmethod
    def get_sensor(cls, column_name, fridge):
        query = select(cls).where(
            cls.fridge_supp == fridge and cls.column_name == column_name
        )
        sensor = db.session.execute(query).scalar_one()
        return sensor
