import json
import datetime
from math import isnan, isinf
from typing import Optional, Iterable, TypeVar
from dataclasses import asdict, fields

from flask import (
    Blueprint,
    Response,
    request,
    g,
)
from flask.views import MethodView

from .db import Fridge, FridgeSupplementary
from .db.abc import FridgeModel


fridge_bp = Blueprint("fridge_data", __name__)


T = TypeVar("T")


def _first(iterable: Iterable[T]) -> T:
    return next(iter(iterable))


class FridgeView(MethodView):
    def _get_data_source(self, fridge_name: str, supp: str) -> Optional[FridgeModel]:
        try:
            g.fridge = Fridge.get_fridge_by_name(fridge_name)
            if supp is not None:
                g.fridge_supp = FridgeSupplementary.get_fridge_supp_by_name(
                    g.fridge, supp
                )
                return g.fridge_supp
            else:
                g.fridge_supp = None
                return g.fridge
        except KeyError:
            return None

    def _sensors_view(self, data_source: FridgeModel):
        """
        Return a list of sensors and their friendly label
        """
        data = []
        for sensor in data_source.sensors:
            data.append(
                {
                    "name": sensor.display_name,
                    "column_name": sensor.column_name,
                }
            )

        r = Response(json.dumps(data))
        r.mimetype = "application/json"
        r.headers["Access-Control-Allow-Origin"] = "*"
        return r

    def _current_view(self, data_source: FridgeModel):
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
        r = Response(json.dumps(data))
        r.mimetype = "application/json"
        r.headers["Access-Control-Allow-Origin"] = "*"
        return r

    def _count_view(self, data_source: FridgeModel, count: int=1):
        """
        Return the latest "n" fields from the data
        """
        fridge_table = data_source.fridge_table()
        latest_n_data = fridge_table.get_last(count)

        # Format the data correctly
        data = {}
        columns = []
        for field in fields(fridge_table):
            data[field.name] = []
            if field.name != "time":
                columns.append(field.name)
        for row in latest_n_data:
            data["time"].append(row.time.isoformat())
            for field in columns:
                field_data = getattr(row, field)
                if field_data is not None and (isnan(field_data) or isinf(field_data)):
                    field_data = None
                data[field].append(field_data)

        # Construct response
        r = Response(json.dumps(data))
        r.mimetype = "application/json"
        r.headers["Access-Control-Allow-Origin"] = "*"
        return r

    def get(self, fridge_name, supp):
        data_source = self._get_data_source(fridge_name, supp)
        if data_source is None:
            return Response(
                f"Unable to find fridge {fridge_name}, supp: {supp}.", status=404
            )

        if "sensors" in request.args:
            return self._sensors_view(data_source)
        elif "current" in request.args:
            return self._current_view(data_source)
        elif "count" in request.args:
            try:
                count = int(request.args["count"])
                return self._count_view(data_source, count)
            except ValueError:
                return Response(
                    f"Count must be a positive integer. Got {request.args[count]}",
                    status=400
                )
        else:
            return Response("Unknown request", status=421)

    def post(self, fridge_name, supp):
        data_source = self._get_data_source(fridge_name, supp)
        valid_sensors = set(sensor.name for sensor in data_source.sensors)

        # Put the data in a json array
        data = {}
        for field, value in request.form.items():
            if field not in valid_sensors:
                return Response(
                    f"Sensor {field} not found in {data_source.name}", status=400
                )
            data[field] = value

        # Make sure time is converted to a timestamp
        if "Time" in data:
            data["Time"] = datetime.fromtimestamp(float(data["Time"]))

        # Add to db
        data_source.fridge_table().append(**data)

        return Response("OK")


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
