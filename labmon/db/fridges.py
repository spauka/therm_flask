import string
from typing import Iterable, Optional, TYPE_CHECKING
from sqlalchemy import Unicode, UnicodeText, Identity, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy.exc import NoResultFound

from .db import db
from .abc import FridgeModel

if TYPE_CHECKING:
    from .abc import SensorModel
    from .sensors import Sensor, SensorSupplementary


class Fridge(FridgeModel):
    fridge_id: Mapped[int] = mapped_column("id", Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(255), unique=True)
    label: Mapped[str] = mapped_column(Unicode(255))
    table_name: Mapped[str] = mapped_column("fridge_table_name", Unicode(255), unique=True)
    comment: Mapped[str] = mapped_column(UnicodeText)
    sensors: Mapped[list["Sensor"]] = relationship(  # type: ignore
        back_populates="fridge", order_by="Sensor.view_order"
    )
    supplementary: Mapped[list["FridgeSupplementary"]] = relationship(back_populates="fridge")
    __tablename__ = "fridges"

    def __init__(
        self,
        name: str,
        table_name: Optional[str] = None,
        sensors: Iterable["Sensor"] = (),
        comment="",
    ):
        self.name = name
        # Derive a table name if not given
        if table_name is None:
            table_name = self._sanitize_name(name)
        self.fridge_table_name = table_name
        for sensor in sensors:
            self.sensors.append(sensor)
        self.comment = comment

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitize a name to a format acceptable for table names
        """
        return "".join(
            c.lower() if c in string.ascii_letters + string.digits else "_" for c in name
        )

    @classmethod
    def get_fridge_by_name(cls, name: str) -> "Fridge":
        """
        Return a fridge object from the given name
        """
        try:
            query = select(cls).where(cls.name == name)
            fridge = db.session.execute(query).scalar_one()
            return fridge
        except NoResultFound as exc:
            raise KeyError(f"Fridge {name} not found") from exc

    def get_supp_by_name(self, name: str) -> "FridgeSupplementary":
        """
        Return a supplementary sensor attached to this fridge
        """
        return FridgeSupplementary.get_fridge_supp_by_name(self, name)


class FridgeSupplementary(FridgeModel):
    supp_id: Mapped[int] = mapped_column("id", Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(1024))
    label: Mapped[str] = mapped_column(Unicode(1024))
    table_name: Mapped[str] = mapped_column("supp_table_name", Unicode(1024))
    fridge_id: Mapped[int] = mapped_column(ForeignKey("fridges.id"))
    fridge: Mapped["Fridge"] = relationship(repr=False)
    sensors: Mapped[list["SensorSupplementary"]] = relationship(  # type: ignore
        back_populates="fridge_supp", order_by="SensorSupplementary.view_order"
    )
    comment: Mapped[str] = mapped_column(UnicodeText())
    __tablename__ = "fridges_supplementary"

    def __init__(
        self,
        name: str,
        table_name: str,
        label: str,
        sensors: Iterable["SensorSupplementary"] = (),
        comment: str = "",
    ):
        self.supp_name = name
        self.table_name = table_name
        self.label = label
        for sensor in sensors:
            self.sensors.append(sensor)
        self.comment = comment

    @classmethod
    def get_fridge_supp_by_name(cls, fridge: Fridge, name: str) -> "FridgeSupplementary":
        """
        Return a supplementary fridge object from the given name
        """
        try:
            query = select(cls).where(cls.fridge == fridge, cls.name == name)
            res = db.session.execute(query)
            supp = res.scalar_one()
            return supp
        except NoResultFound as exc:
            raise KeyError(f"Supplementary fridge {name} not found") from exc
