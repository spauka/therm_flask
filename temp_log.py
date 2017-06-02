import config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_sqlalchemy
sa = flask_sqlalchemy.sqlalchemy

db = SQLAlchemy()

import string
from itertools import islice
from datetime import datetime

class SensTable(object):
    def __len__(self):
        cnt = self._table().count()
        return db.session.execute(cnt).first()[0]

    def __getitem__(self, key):
        count = len(self)
        if isinstance(key, slice):
            if (key.start is not None and not isinstance(key.start, int)) \
               or (key.stop is not None and not isinstance(key.stop, int)):
                raise TypeError('Start and end indices must be numeric')

            start = key.start
            stop = key.stop
            step = key.step
            limit = None

            if start is not None and start < 0:
                start = count+start
            if stop is not None and stop < 0:
                stop = count+stop-1
            if start is not None and stop is not None:
                limit = stop-start
                if limit < 0:
                    return iter([])

            res = self._table().select(offset=start, limit=limit)
            if step is None:
                res = res.order_by(self._table().c.Time.asc())
                res = db.session.execute(res)
                return iter(res)
            else:
                if step < 0:
                    res = res.order_by(self._table().c.Time.desc())
                    step = abs(step)
                else:
                    res = res.order_by(self._table().c.Time.asc())
                res = db.session.execute(res)
                return islice(res, None, None, step)
        elif isinstance(key, int):
            if key >= count:
                raise IndexError('List index out of range')
            if key < 0:
                key = count + key
            res = self._table().select(offset=key, limit=1).order_by(self._table().c.Time.asc())
            res = db.session.execute(res)
            return res.first()
        else:
            raise TypeError('List indices must be int')

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError('List index must be int')
        if key < 0:
            key = len(self)+key

        if key >= len(self):
            raise IndexError('List index out of range')
        res = self[key]
        stmt = self._table().update().where(self._table().c.Time==res['Time']).values(**value)
        db.session.execute(stmt)
        db.session.commit()

    def __delitem__(self, key):
        items = self[key]
        if isinstance(key, int):
            items = [items]
        items = list(items)
        for i in items:
            stmt = self._table().delete().where(self._table().c.Time==i['Time'])
            db.session.execute(stmt)
        db.session.commit()

    def __iter__(self):
        return iter(self[:])

    def __reversed__(self):
        return iter(self[::-1])

    def append(self, **values):
        if "Time" in values:
            time = values["Time"]
            del values["Time"]
        else:
            time = datetime.now()

        # Ensure we are adding only to valid thermometers
        for therm, value in values.iteritems():
            therm_s = self.get_sensor(therm, self)
        ins = self._table().insert().values(Time=time, **values)
        db.session.execute(ins)
        db.session.commit()

    def remove(self):
        stmt = self._table().delete().where(fridge.table().c.Time == i['Time'])
        db.session.execute(stmt)
        db.session.commit()

    def hourly_avg(self, sensor):
        columns = self._table().columns
        dategroup = sa.func.date_trunc('hour', sa.func.timezone('UTC', columns.Time)).label("Time")
        dategroup.type = sa.DateTime()
        if sensor not in columns:
            raise KeyError("Sensor not found")
        sensor_c = sa.func.avg(columns[sensor]).label(sensor)
        query = sa.select((dategroup, sensor_c)).group_by(dategroup).order_by(dategroup.asc())
        return db.session.execute(query)

    def range(self, start, stop):
        query = self._table().select().where(self._table().columns.Time.between(start, stop)).order_by(self._table().columns.Time.asc())
        return db.session.execute(query)

class Sensors(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fridge_id = db.Column(db.Integer(), db.ForeignKey('Fridges.id'))
    column_name = db.Column(db.String(1024))
    name = db.Column(db.String(1024))
    view_order = db.Column(db.Integer())
    visible = db.Column(db.Integer())
    __tablename__ = "Sensors"

    def __init__(self, name, fridge, view_order=1, visible=1):
        if isinstance(fridge, Fridges):
            self.fridge_id = fridge.id
        else:
            self.fridge_id = int(fridge)
        self.name = name
        self.column_name = name
        self.view_order = view_order
        self.visible = visible

    def __repr__(self):
        return "<Sensor %r>" % (self.name)

    @classmethod
    def get_sensor(cls, name, fridge, add=False):
        if isinstance(fridge, Fridges):
            fridge_id = fridge.id
        else:
            fridge_id = int(fridge)

        sensor = cls.query.filter_by(column_name=name, fridge_id=fridge_id)
        if sensor.count() == 0 and add:
            sensor = Sensors(name, fridge)
            db.session.add(sensor)
            return sensor
        elif sensor.count() == 0 and not add:
            return None
        return sensor.first()

class Sensors_Supplementary(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fridge_suppl_id = db.Column(db.Integer(), db.ForeignKey('Fridges_Supplementary.id'))
    column_name = db.Column(db.String(1024))
    name = db.Column(db.String(1024))
    view_order = db.Column(db.Integer())
    visible = db.Column(db.Integer())
    __tablename__ = "Sensors_Supplementary"

    def __init__(self, name, fridge_suppl, column_name=None, view_order=1, visible=1):
        if isinstance(fridge_suppl, Fridges_Supplementary):
            self.fridge_suppl_id = fridge_suppl.id
        else:
            self.fridge_suppl_id = int(fridge_suppl)
        self.name = name
        if column_name:
            self.column_name = column_name
        else:
            self.column_name = name
        self.view_order = view_order
        self.visible = visible

    def __repr__(self):
        return "<Supplementary_Sensor %r>" % (self.name)

    @classmethod
    def get_sensor(cls, name, fridge, add=False):
        if isinstance(fridge, Fridges_Supplementary):
            suppl_id = fridge.id
        else:
            suppl_id = int(fridge)

        sensor = cls.query.filter_by(column_name=name, fridge_suppl_id=suppl_id)
        if sensor.count() == 0 and add:
            sensor = Sensors_Supplementary(name, fridge, name)
            db.session.add(sensor)
            return sensor
        elif sensor.count() == 0 and not add:
            return None
        return sensor.first()

class Fridges_Supplementary(db.Model, SensTable):
    id = db.Column(db.Integer(), primary_key=True)
    fridge_id = db.Column(db.Integer(), db.ForeignKey('Fridges.id'))
    table_name = db.Column(db.String(1024))
    name = db.Column(db.String(1024))
    label = db.Column(db.String(1024))
    comment = db.Column(db.UnicodeText())
    sensors = db.relationship('Sensors_Supplementary', backref='fridge_suppl', lazy='dynamic')
    get_sensor = Sensors_Supplementary.get_sensor
    __tablename__ = "Fridges_Supplementary"

    def __init__(self, name, table_name, label, sensors, comment=None):
        self.table_name = table_name
        self.name = name
        self.label = label
        for sensor in sensors:
            self.sensors.append(Sensors_Supplementary.get_sensor(sensor, self, True))
        self.comment = comment

    def __repr__(self):
        return "<Supplementary for %r: %r>" % (self.fridge, self.table_name)

    def suppl_table(self):
        # Sanitize name by replacing all spacial characters
        if self.table_name in db.metadata.tables:
            return db.metadata.tables[self.table_name]
        elif not hasattr(self, '_suppl_table') or self._suppl_table is None:
            self._suppl_table = db.Table(self.table_name, db.metadata,
                                         db.Column('Time', db.DateTime, primary_key=True),
                                         *[db.Column(sensor.column_name, db.Float) for sensor in self.sensors])
            return self._suppl_table

    _table=suppl_table

class Fridges(db.Model, SensTable):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    comment = db.Column(db.UnicodeText())
    sensors = db.relationship('Sensors', backref='fridge', lazy='dynamic')
    supplementary = db.relationship('Fridges_Supplementary', backref='fridge', lazy='dynamic')
    get_sensor = Sensors.get_sensor
    __tablename__ = "Fridges"

    # Cache of existing table definitions
    __tables__ = {}

    def __init__(self, name, sensors, comment=None):
        self.name = name
        for sensor in sensors:
            self.sensors.append(Sensors.get_sensor(sensor, self, True))
        self.comment = comment if comment is not None else ""
        self._fridge_table = None

    def __repr__(self):
        return "<Fridge %r>" % self.name

    def fridge_table(self):
        # Sanitize name by replacing all spacial characters
        if self.table_name in db.metadata.tables:
            return db.metadata.tables[self.table_name]
        elif not hasattr(self, '_fridge_table') or self._fridge_table is None:
            name = "".join(c if c in string.ascii_letters+string.digits else "_" for c in self.name)
            self._fridge_table = db.Table(name, db.metadata,
                                          db.Column('Time', db.DateTime, primary_key=True),
                                          *[db.Column(therm.column_name, db.Float) for therm in self.sensors])
            return self._fridge_table

    _table = fridge_table

if __name__ == "__main__":
    from app import app
    # Bind db
    db.app = app
    db.init_app(app)

    # Bootstrap table and data creation
    db.create_all()

    # Generate a default list of fridges, and thermometers on those fridges
    thermometers = ["MC_PT", "MC_Speer", "50mK_RuO", "Still_RuO", "4K_RuO"]
    fridges = ["Big_Fridge"]
    fridge_models = []

    # Create tables for those fridges
    for fridge in fridges:
        fridge_model = Fridges(name=fridge, thermometers=thermometers)
        fridge_table = fridge_model.fridge_table()
        fridge_models.append(fridge_model)

    # Then, create all the new tables
    db.create_all()
    # And finally, add all models
    for fridge in fridge_models:
        db.session.add(fridge)
    db.session.commit()

