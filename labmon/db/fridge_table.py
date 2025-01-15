from datetime import datetime

from . import SQLAlchemy, db

class FridgeTable:
    def __init__(self):
        pass

    def fridge_table(self):
        raise NotImplementedError("Fridge table not yet resolved")

    def __len__(self):
        cnt = self.fridge_table().count()
        return db.session.execute(cnt).first()[0]

    def append(self, **values):
        if "Time" in values:
            time = values["Time"]
            del values["Time"]
        else:
            time = datetime.now()

        try:
            ins = self.fridge_table().insert().values(Time=time, **values)
            db.session.execute(ins)
            db.session.commit()
        except SQLAlchemy.exc.CompileError as exc:
            raise KeyError("Invalid column name") from exc
        except SQLAlchemy.exc.IntegrityError:
            # This occurs if we try and add a duplicate timestamp
            # We can fail quietly here
            return False

    def remove(self):
        stmt = self.fridge_table().delete().where(self.fridge_table().c.Time == ['Time'])
        db.session.execute(stmt)
        db.session.commit()

    def hourly_avg(self, sensor):
        columns = self.fridge_table().columns
        dategroup = SQLAlchemy.func.date_trunc('hour', SQLAlchemy.func.timezone('UTC', columns.Time)).label("Time")
        dategroup.type = SQLAlchemy.DateTime()
        if sensor not in columns:
            raise KeyError("Sensor not found")
        sensor_c = SQLAlchemy.func.avg(columns[sensor]).label(sensor)
        query = SQLAlchemy.select((dategroup, sensor_c)).group_by(dategroup).order_by(dategroup.asc())
        return db.session.execute(query)

    def range(self, start, stop):
        query = self.fridge_table().select().where(self.fridge_table().columns.Time.between(start, stop)).order_by(self.fridge_table().columns.Time.asc())
        return db.session.execute(query)
