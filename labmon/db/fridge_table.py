from datetime import datetime
from sqlalchemy import Column, Table, DateTime, select, insert, func

from . import SQLAlchemy, db

class SensorReading:
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

    @classmethod
    def __len__(cls):
        query = select(func.count()).select_from(cls)
        return db.session.scalar(query)

    @classmethod
    def append(cls, **values):
        if "Time" in values:
            time = values["Time"]
            del values["Time"]
        else:
            time = datetime.now()

        try:
            query = insert(cls).values(time=time, **values)
            db.session.execute(query)
            db.session.commit()
        except SQLAlchemy.exc.CompileError as exc:
            raise KeyError("Invalid column name") from exc
        except SQLAlchemy.exc.IntegrityError:
            # This occurs if we try and add a duplicate timestamp
            # We can fail quietly here
            return False

    @classmethod
    def get_last(cls, n: int=1):
        """
        Return the most recent `n` sensor readings. If n is greater than the number
        of readings stored, return the all the readings.
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer. Got {n}.")
        query = select(cls).order_by(cls.time.desc()).limit(n)
        #subq = query.subquery()
        #ordered_query = select(subq).order_by(subq.c.time.asc())
        #res = db.session.execute(ordered_query)
        res = db.session.execute(query)
        return iter(res)

    @classmethod
    def get_between(cls, start: datetime, stop: datetime):
        """
        Return sensor readings taken between the start and stop times
        """
        query = select(cls).where(cls.time.between(start, stop)).order_by(cls.time.desc())
        subq = query.subquery()
        ordered_query = select(subq).order_by(subq.c.time.asc())
        res = db.session.execute(ordered_query)
        return iter(res)

    @classmethod
    def hourly_avg(cls, sensor):
        """
        Return hourly average
        TODO: Rewrite for timescaledb functions
        """
        dategroup = func.date_trunc('hour', func.timezone('UTC', cls.time)).label("Time")
        dategroup.type = DateTime()
        if sensor not in cls.__table__.c:
            raise KeyError("Sensor not found")
        sensor_q = func.avg(cls.__table__.c[sensor]).label(sensor)
        # Construct the query. Note we don't worry about ordering descending since we are returning
        # the entire dataset.
        query = select(dategroup, sensor_q).group_by(dategroup).order_by(dategroup.asc())
        return iter(db.session.execute(query))
