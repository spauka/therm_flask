from dataclasses import Field, fields
from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy import TIMESTAMP, Column, func, insert, select, Table
from sqlalchemy.orm import aliased
from sqlalchemy.exc import CompileError, IntegrityError

from .db import db


class SensorReading:
    """
    Table of sensor readings
    Note that the table has an index on time descending, so where possible queries
    are done on that index and then sorted in a subquery if they should be ordered
    ascending. This is far more efficient than doing an ascending query as it removes
    the need to do a full scan over the table/index to obtain a count.
    """

    # All fridges have a Time column
    __abstract__ = True
    __table__: Table
    __dataclass_fields__: dict[str, Field]
    time: Column

    def __init__(self):
        pass

    def __repr__(self):
        columns = self.__table__.columns
        values = ", ".join((f"{c.name}={getattr(self, c.name)!r}" for c in columns))
        return f"{self.__class__.__name__}({values})"

    @classmethod
    def size(cls):
        query = select(func.count()).select_from(cls)  # pylint: disable=not-callable
        return db.session.scalar(query)

    @classmethod
    def append(cls, **values) -> bool:
        # Handle both "Time" and "time" for legacy reasons
        if "Time" in values:
            time = values["Time"]
            del values["Time"]
        elif "time" in values:
            time = values["time"]
            del values["time"]
        else:
            time = datetime.now().astimezone()

        try:
            query = insert(cls).values(time=time, **values)
            db.session.execute(query)
            db.session.commit()
            return True
        except CompileError as exc:
            raise KeyError("Invalid column name") from exc
        except IntegrityError:
            # This occurs if we try and add a duplicate timestamp
            # We can fail quietly here
            return False

    @classmethod
    def get_last(cls, n: int = 1) -> Iterable["SensorReading"]:
        """
        Return the most recent `n` sensor readings. If n is greater than the number
        of readings stored, return the all the readings.
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer. Got {n}.")
        query = select(cls).order_by(cls.time.desc()).limit(n)
        subq = aliased(cls, query.subquery())
        ordered_query = select(subq).order_by(subq.time.asc())
        res = db.session.execute(ordered_query)
        return res.scalars()

    @classmethod
    def get_between(
        cls, start: Optional[datetime] = None, stop: Optional[datetime] = None
    ) -> Iterable["SensorReading"]:
        """
        Return sensor readings taken between the start and stop times
        """
        # Construct the correct select query
        query = select(cls)
        if start is not None and stop is not None:
            query = query.where(cls.time.between(start, stop))
        elif start is not None:
            query = query.where(cls.time > start)
        elif stop is not None:
            query = query.where(cls.time < stop)
        else:
            raise ValueError("Either start, stop or both must be given")
        query = query.order_by(cls.time.desc())

        # Order data by time ascending
        subq = aliased(cls, query.subquery())
        ordered_query = select(subq).order_by(subq.time.asc())
        res = db.session.execute(ordered_query)
        return res.scalars()

    @classmethod
    def hourly_avg(
        cls,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        count: Optional[int] = None,
    ) -> Iterable["SensorReading"]:
        """
        Return hourly average
        TODO: Rewrite for timescaledb functions
        """
        return cls.avg_data("hour", start, stop, count)

    @classmethod
    def avg_data(
        cls,
        time_period: str = "hour",
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        count: Optional[int] = None,
    ) -> Iterable["SensorReading"]:
        """
        Averaged data over a time period given by time_period
        This can be "hour", "day", or "month" (or year but this is kind of useless)
        TODO: Rewrite for timescaledb functions
        """
        dategroup = func.date_trunc(time_period, cls.time).label("time")
        dategroup.type = TIMESTAMP(timezone=True)
        table_fields = []
        for field in fields(cls):
            name = field.name
            if name == "time":
                continue
            table_fields.append(func.avg(getattr(cls, name)).label(name))

        # Construct the query
        query = select(dategroup, *table_fields)
        if start is not None and stop is not None:
            query = query.where(dategroup.between(start, stop))
        elif start is not None:
            query = query.where(dategroup > start)
        elif stop is not None:
            query = query.where(dategroup < stop)
        if count is not None:
            query = query.limit(count)
        query = query.group_by(dategroup).order_by(dategroup.desc())

        subq = aliased(cls, alias=query.subquery(), adapt_on_names=True)
        ordered_query = select(subq).order_by(subq.time)
        res = db.session.execute(ordered_query)
        return res.scalars()
