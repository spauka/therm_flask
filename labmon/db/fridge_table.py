from datetime import datetime
from sqlalchemy import Column, Table, DateTime, select, insert, func

from . import SQLAlchemy, db

class FridgeTable:
    """
    Table of sensor readings
    Note that the table has an index on time descending, so where possible queries are done on that index
    and then sorted in a subquery if they should be ordered ascending. This is far more efficient than doing
    an ascending query as it removes the need to do a full scan over the table/index to obtain a count.
    """
    # All fridges have a Time column
    time: Column
    __table__: Table

    def __init__(self):
        pass

    def fridge_table(self):
        raise NotImplementedError("Fridge table not yet resolved")

    def __len__(self):
        query = select(func.count()).select_from(self)
        return db.session.scalar(query)

    def append(self, **values):
        if "Time" in values:
            time = values["Time"]
            del values["Time"]
        else:
            time = datetime.now()

        try:
            query = insert(self).values(time=time, **values)
            db.session.execute(query)
            db.session.commit()
        except SQLAlchemy.exc.CompileError as exc:
            raise KeyError("Invalid column name") from exc
        except SQLAlchemy.exc.IntegrityError:
            # This occurs if we try and add a duplicate timestamp
            # We can fail quietly here
            return False

    def get_last(self, n: int=1):
        """
        Return the most recent `n` sensor readings. If n is greater than the number
        of readings stored, return the all the readings.
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer. Got {n}.")
        query = select(self).order_by(self.time.desc()).limit(n)
        subq = query.subquery()
        ordered_query = select(subq).order_by(subq.c.time.asc())
        res = db.session.execute(ordered_query)
        return iter(res)

    def get_between(self, start: datetime, stop: datetime):
        """
        Return sensor readings taken between the start and stop times
        """
        query = select(self).where(self.time.between(start, stop)).order_by(self.time.desc())
        subq = query.subquery()
        ordered_query = select(subq).order_by(subq.c.time.asc())
        res = db.session.execute(ordered_query)
        return iter(res)

    def hourly_avg(self, sensor):
        """
        Return hourly average
        TODO: Rewrite for timescaledb functions
        """
        dategroup = func.date_trunc('hour', func.timezone('UTC', self.time)).label("Time")
        dategroup.type = DateTime()
        if sensor not in self.__table__.c:
            raise KeyError("Sensor not found")
        sensor_q = func.avg(self.__table__.c[sensor]).label(sensor)
        # Construct the query. Note we don't worry about ordering descending since we are returning
        # the entire dataset.
        query = select(dategroup, sensor_q).group_by(dategroup).order_by(dategroup.asc())
        return iter(db.session.execute(query))
