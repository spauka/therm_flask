import json
import datetime
from math import isnan, isinf

from flask import (
    Blueprint,
    Response,
    render_template,
    render_template_string,
    request,
    g,
)
from flask.views import MethodView

from .db import db, Fridge
from .db.abc import FridgeModel


fridge_bp = Blueprint("fridge_data", __name__)


class FridgeView(MethodView):
    def _get_data_source(self, fridge_name: str, supp: str) -> FridgeModel:
        try:
            g.fridge = Fridge.get_by_table_name(fridge_name)
            if supp is not None:
                g.fridge_supp = g.fridge.get_supp_by_name(supp)
                return g.fridge_supp
            else:
                g.fridge_supp = None
                return g.fridge
        except KeyError:
            r = Response(f"Unable to find fridge {fridge_name}, supp: {supp}.")
            r.status_code = 404
            return r
        
    def _sensors_view(self, data_source: FridgeModel):
        data = []
        for sensor in data_source.sensors:
            data.append({
                'name': sensor.display_name,
                'column_name': sensor.column_name,
            })
        
        r = Response(json.dumps(data))
        r.mimetype = "application/json"
        r.headers['Access-Control-Allow-Origin'] = "*"
        return r
    
    def _current_view(self, data_source: FridgeModel):
        latest_data = data_source.fridge_table().get_last(1)
        data = dict(latest_data)
        data["time"] = data["time"].isoformat()
        for k in data:
            if isinstance(data[k], float) and (isinf(data[k]) or isnan(data[k])):
                data[k] = None

    def get(self, fridge_name, supp):
        data_source = self._get_data_source(fridge_name, supp)

        if "sensors" in request.args:
            return self._sensors_view(data_source)
        elif "current" in request.args:
            return self._current_view(data_source)

    def post(self, fridge_name, supp):
        data_source = self._get_data_source(fridge_name, supp)
        valid_sensors = set(sensor.name for sensor in data_source.sensors)

        # Put the data in a json array
        data = {}
        for field, value in request.form.items():
            if field not in valid_sensors:
                r = Response(f"Sensor {field} not found in {data_source.name}")
                r.status_code = 400
                return r
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
    view_func=FridgeView.as_view("fridge_view")
)
fridge_bp.add_url_rule(
    "/<fridge_name>",
    defaults={"supp": None},
    endpoint="fridge_view",
    view_func=FridgeView.as_view("fridge_view"),
)

