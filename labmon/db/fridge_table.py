from datetime import datetime
from itertools import islice

from . import SQLAlchemy, db

class FridgeTable:
    def __init__(self):
        pass

    def fridge_table(self):
        raise NotImplementedError("Fridge table not yet resolved")

    def __len__(self):
        cnt = self.fridge_table().count()
        return db.session.execute(cnt).first()[0]

    def __getitem__(self, key):
        if isinstance(key, slice):
            if (key.start is not None and not isinstance(key.start, int)) \
               or (key.stop is not None and not isinstance(key.stop, int)):
                raise TypeError('Start and end indices must be numeric')

            start = key.start
            stop = key.stop
            step = key.step if key.step else 1
            if step < 0:
                raise ValueError("Negative step sizes are not supported")
            limit = None
            reverse = False

            if start is None:
                if stop is None:
                    return self[0::step]
                if stop < 0:
                    count = len(self)
                    stop = count+stop-1
                return self[0:stop:step]
            elif start < 0:
                if stop is not None:
                    count = len(self)
                    start = count+start
                    if stop < 0:
                        stop = count+stop-1
                    return self[start:stop:step]

                # Otherwise select in reverse order and swap order in python
                res = self.fridge_table().select(limit=abs(start))
                res = res.order_by(self.fridge_table().c.Time.desc())
                reverse = True
            else: # start > 0
                if stop is None:
                    pass # This is the same as limit=None
                elif stop < 0:
                    count = len(self)
                    stop = count+stop-1
                    return self[start:stop:step]
                else:
                    limit = stop-start
                    if limit < 0:
                        return iter(())

                res = self.fridge_table().select(offset=start, limit=limit)
                res = res.order_by(self.fridge_table().c.Time.asc())

            res = db.session.execute(res)

            if reverse:
                res = reversed(tuple(res))

            return islice(res, None, None, step)
        elif isinstance(key, int):
            if key < 0:
                offset = abs(key) - 1
            else:
                offset = key
            res = self.fridge_table().select(offset=offset, limit=1)
            if key >= 0:
                res = res.order_by(self.fridge_table().c.Time.asc())
            else:
                res = res.order_by(self.fridge_table().c.Time.desc())
            res = db.session.execute(res)
            res = res.first()
            if res is None:
                raise KeyError("Index out of range")
            return res
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
        stmt = self.fridge_table().update().where(self.fridge_table().c.Time==res['Time']).values(**value)
        db.session.execute(stmt)
        db.session.commit()

    def __delitem__(self, key):
        items = self[key]
        if isinstance(key, int):
            items = [items]
        items = list(items)
        for i in items:
            stmt = self.fridge_table().delete().where(self.fridge_table().c.Time==i['Time'])
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
