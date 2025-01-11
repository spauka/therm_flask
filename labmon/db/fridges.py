import string

from . import db, Sensors, SensorsSupplementary
from .fridge_table import FridgeTable


class Fridges(db.Model, FridgeTable):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    comment = db.Column(db.UnicodeText())
    sensors = db.relationship('Sensors', backref='fridge', lazy='dynamic')
    supplementary = db.relationship('Fridges_Supplementary', backref='fridge', lazy='dynamic')
    __tablename__ = "fridges"

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
        res = Fridges.query.filter(Fridges.name==name).first()
        if res is None:
            raise KeyError("Unable to find fridge")
        return res


class FridgesSupplementary(db.Model, FridgeTable):
    id = db.Column(db.Integer(), primary_key=True)
    fridge_id = db.Column(db.Integer(), db.ForeignKey('Fridges.id'))
    table_name = db.Column(db.String(1024))
    name = db.Column(db.String(1024))
    label = db.Column(db.String(1024))
    comment = db.Column(db.UnicodeText())
    sensors = db.relationship('Sensors_Supplementary', backref='fridge_suppl', lazy='dynamic')
    _suppl_table = None
    __tablename__ = "fridges_supplementary"

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
