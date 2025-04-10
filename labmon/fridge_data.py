from dataclasses import asdict, fields
from datetime import datetime, timedelta
from math import isinf, isnan
from typing import Iterable, Optional, TypeVar

from flask import Blueprint, Response, g, request
from flask.json import jsonify
from flask.views import MethodView

from .db import Fridge, FridgeSupplementary
from .db.abc import FridgeModel, SensorReading

fridge_bp = Blueprint("fridge_data", __name__)


T = TypeVar("T")


def _first(iterable: Iterable[T]) -> T:
    return next(iter(iterable))


class FridgeView(MethodView):
    def _get_data_source(self, fridge_name: str, supp: Optional[str]) -> Optional[FridgeModel]:
        try:
            g.fridge = Fridge.get_fridge_by_name(fridge_name)
            if supp is not None:
                g.fridge_supp = FridgeSupplementary.get_fridge_supp_by_name(g.fridge, supp)
                g.fridge_table = g.fridge_supp.fridge_table()
                return g.fridge_supp
            g.fridge_supp = None
            g.fridge_table = g.fridge.fridge_table()
            return g.fridge
        except KeyError:
            return None

    def _sensors_view(self, data_source: FridgeModel) -> Response:
        """
        Return a list of sensors and their friendly label
        """
        data = []
        for sensor in data_source.sensors:
            if not sensor.visible:
                continue
            data.append(
                {
                    "name": sensor.display_name,
                    "column_name": sensor.column_name,
                    "view_order": sensor.view_order,
                }
            )

        r = jsonify(data)
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Cache-Control"] = "public, max-age=300"
        return r

    def _current_view(self, data_source: FridgeModel) -> Response:
        """
        Return the current data from the fridge
        """
        latest_data = _first(data_source.fridge_table().get_last(1))
        data = asdict(latest_data)
        data["time"] = data["time"].isoformat()
        for k in data:
            if isinstance(data[k], float) and (isinf(data[k]) or isnan(data[k])):
                data[k] = None

        # Construct response
        r = jsonify(data)
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Cache-Control"] = "public, max-age=5"
        return r

    def _summary_view(self, data_source: FridgeModel) -> Response:
        """
        Try to return a useful summary of the most useful thermometer associated with
        a data source. By default, we return the last 2 hours of data.
        """
        sensors = data_source.sensors
        stop = datetime.now().astimezone()
        start = stop - timedelta(hours=2)
        latest_data = data_source.fridge_table().get_between(start, stop)

        # For most situations, the coldest thermometer is usually the right one to return
        # Let's preprocess out the minimum value from the sensor.
        summary_data: list[Optional[float]] = []
        for data in latest_data:
            min_val = float("inf")
            for sensor in sensors:
                # Time is not sensor data
                if sensor.column_name == "time":
                    continue
                val = getattr(data, sensor.column_name)
                # Ignore NaN or inf values
                if val is None or isnan(val) or isinf(val) or val == 0:
                    continue
                min_val = min(min_val, val)
            # If we didn't find any readings, add None
            if isinf(min_val):
                summary_data.append(None)
            else:
                summary_data.append(min_val)

        # Construct response
        r = jsonify(summary_data)
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Cache-Control"] = "public, max-age=5"
        return r

    def _format_data(
        self, fridge_table: type[SensorReading], rows: Iterable[SensorReading]
    ) -> dict[str, list]:
        # Format the data correctly
        data: dict[str, list[Optional[float]]] = {}
        columns = []
        for field in fields(fridge_table):
            data[field.name] = []
            if field.name != "time":
                columns.append(field.name)
        for row in rows:
            data["time"].append(row.time.isoformat())
            for field_name in columns:
                field_data = getattr(row, field_name)
                if field_data is not None and (isnan(field_data) or isinf(field_data)):
                    field_data = None
                data[field_name].append(field_data)

        return data

    def _count_view(
        self, data_source: FridgeModel, count: int = 1, avg_period: Optional[str] = None
    ) -> Response:
        """
        Return the latest "n" fields from the data
        """
        fridge_table = data_source.fridge_table()
        if avg_period is None:
            latest_n_data = fridge_table.get_last(count)
        else:
            latest_n_data = fridge_table.avg_data(avg_period, count=count)
        data = self._format_data(fridge_table, latest_n_data)

        # Construct response
        r = jsonify(data)
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Cache-Control"] = "public, max-age=30"
        return r

    def _date_view(
        self,
        data_source: FridgeModel,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        avg_period: Optional[str] = None,
    ) -> Response:
        fridge_table = data_source.fridge_table()
        if avg_period is None:
            fridge_data = fridge_table.get_between(start, stop)
        else:
            fridge_data = fridge_table.avg_data(avg_period, start, stop)
        data = self._format_data(fridge_table, fridge_data)

        # Construct response
        r = jsonify(data)
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Cache-Control"] = "public, max-age=300"
        return r

    def get(self, fridge_name, supp) -> Response:
        data_source = self._get_data_source(fridge_name, supp)
        if data_source is None:
            return Response(f"Unable to find fridge {fridge_name}, supp: {supp}.", status=404)

        avg_period = request.args.get("avg_period", None)
        if avg_period is not None:
            if avg_period not in ("hour", "day", "month"):
                return Response(
                    (
                        "Data can only be summarized by 'hour', 'day' or 'month'. "
                        f"Requested {avg_period}."
                    ),
                    status=400,
                )

        if "sensors" in request.args:
            return self._sensors_view(data_source)
        if "current" in request.args:
            return self._current_view(data_source)
        if "summary" in request.args:
            return self._summary_view(data_source)
        if "count" in request.args:
            try:
                count = int(request.args["count"])
            except ValueError:
                return Response(
                    f"Count must be a positive integer. Got {request.args['count']}",
                    status=400,
                )
            return self._count_view(data_source, count, avg_period=avg_period)
        if "start" in request.args and "stop" in request.args:
            try:
                try:
                    start = datetime.fromisoformat(request.args["start"])
                except ValueError:
                    start_timestamp = float(request.args["start"])
                    # Detect javascript timestamps
                    if start_timestamp > 10_000_000_000:
                        start_timestamp /= 1000
                    start = datetime.fromtimestamp(start_timestamp)
                try:
                    stop = datetime.fromisoformat(request.args["stop"])
                except ValueError:
                    stop_timestamp = float(request.args["stop"])
                    if stop_timestamp > 10_000_000_000:
                        stop_timestamp /= 1000
                    stop = datetime.fromtimestamp(stop_timestamp)
            except ValueError:
                return Response("Invalid start or stop date.", status=400)

            if start >= stop:
                return Response(
                    f"Start occurs after stop ({start.isoformat()} - {stop.isoformat()})",
                    status=400,
                )
            if stop - start > timedelta(days=30) and avg_period is None:
                return Response(
                    (
                        "An averaging period must be given for intervals longer than 30 days. "
                        f"Requested interval: {str(stop - start)}"
                    ),
                    status=400,
                )

            return self._date_view(data_source, start, stop, avg_period=avg_period)
        if "start" in request.args or "stop" in request.args:
            return Response(
                "Both start and stop must be provided when requesting a date range",
                status=400,
            )
        if avg_period is not None:
            # Can also return all data if we're asking for averaged data
            return self._date_view(data_source, avg_period=avg_period)

        return Response("Unknown request", status=421)

    def post(self, fridge_name, supp) -> Response:
        data_source = self._get_data_source(fridge_name, supp)
        if data_source is None:
            return Response(f"Unable to find fridge {fridge_name}, supp: {supp}.", status=404)

        valid_sensors = set(sensor.column_name for sensor in data_source.sensors)

        # Put the data in a json array
        data: dict[str, float | datetime] = {}
        for field_name, value in request.form.items():
            # Convert all variants of time to lowercase time, and convert into timestamp
            if field_name.lower() == "time":
                try:
                    data["time"] = datetime.fromisoformat(value)
                except ValueError:
                    try:
                        data["time"] = datetime.fromtimestamp(float(value))
                    except ValueError:
                        return Response(f"Invalid time format: {data['time']}", status=400)
            elif field_name not in valid_sensors:
                return Response(f"Sensor {field_name} not found in {data_source.name}", status=400)
            else:
                try:
                    data[field_name] = float(value)
                except ValueError:
                    return Response(f"Invalid value for field {field_name}: {value!r}", status=400)

        # Add to db
        try:
            result = data_source.fridge_table().append(**data)
            if result:
                return Response("OK")
            return Response("OK but duplicate")
        except KeyError as e:
            return Response(str(e), status=400)


fridge_bp.add_url_rule(
    "/<fridge_name>/supp/<supp>",
    endpoint="fridge_supp_view",
    view_func=FridgeView.as_view("fridge_view"),
)
fridge_bp.add_url_rule(
    "/<fridge_name>",
    defaults={"supp": None},
    endpoint="fridge_view",
    view_func=FridgeView.as_view("fridge_view"),
)
