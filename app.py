import config

from flask import Flask, request, render_template, render_template_string, Response, make_response
from flask_sqlalchemy import SQLAlchemy

from temp_log import *

import logging
from logging import FileHandler
import json
from time import mktime, gmtime
from datetime import datetime, timedelta
from math import isnan, isinf

import os
from os import listdir
import os.path

app = Flask("Thermometry", static_url_path="/static")
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = config.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.track_modifications

db.init_app(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

#@app.route('/static/<path:static>/')
#def static(static):
#    return Response(static)

@app.route('/<fridge_name>/<data_type>/', defaults={'sensor': None}, methods=['GET', 'POST'])
@app.route('/<fridge_name>/<data_type>/<sensor>')
def get_data(fridge_name, data_type, sensor):
    # First pull up the relevant fridge
    fridge_name = fridge_name.replace('_', ' ')
    fridge = Fridges.query.filter_by(name=fridge_name)
    if fridge.count() == 0:
        r = Response(render_template_string('Unable to find fridge {{fridge}}.', fridge=fridge))
        r.status_code = 404
        return r
    fridge = fridge.first()

    # Are we looking for a supplementary field?
    if data_type != 'data':
        sup = fridge.supplementary.filter_by(name=data_type)
        if sup.count() == 0:
            r = Response(render_template_string('Unable to find supplementary set {{suppl}}.', suppl=data_type))
            r.status_code = 404
            return r
        sup = sup.first()
        source = sup
    else:
        sup = None
        source = fridge

    # Check whether we are trying to put new data in to the database
    if request.method == 'POST':
        return Response(insert_data(fridge, sup))

    if 'count' in request.args:
        try:
            count = int(request.args['count'])
        except ValueError:
            count = 1000
    else:
        count = 1000

    if any(x in ['legacy', 'single'] for x in request.args): # We only support fridges for this type of request
        data_raw = fridge[-count:]
        data = []
        for row in data_raw:
            data.append((row['Time'], 
                         0, row["Four_K_RuO"],
                         0, row["Still_RuO"],
                         0, row["50mK_RuO"],
                         0, row["MC_CMN"],
                         0, row["MC_PT"]))
            if 'single' in request.args:
                data[-1] = data[-1] + (0, row["four_K_PT_front"])
        try:
            if 'legacy' in request.args:
                return Response(render_template("data_legacy.csv", data=data), mimetype='text/plain')
            else:
                return Response(render_template("data_single.csv", data=data), mimetype='text/plain')
        except Exception as e:
            return repr(e)
    elif 'sensors' in request.args:
        data = [{'name': x.name, 'column_name': x.column_name} for x in source.sensors.filter_by(visible=1).order_by("view_order")]
    elif 'summary' in request.args:
        data_raw = source[-30:]
        data = []
        for row in data_raw:
            if 'MC_Pt' in row:
                if row['MC_Pt'] > 20000 and row['MC_Pt'] < 500000:
                    data.append(row['MC_Pt'])
                elif row['MC_Speer'] < 4000:
                    data.append(row['MC_Speer'])
                else:
                    data.append(row['Four_K_RuO'])
            elif 'ProbeTemp' in row:
                data.append(float(row['ProbeTemp'])*1000)
            else:
                if row['Four_K_Pt'] < 20000:
                    data.append(row['Four_K_RuO'])
                else:
                    data.append(row['Four_K_Pt'])
    elif 'current' in request.args:
        try:
            data = source[-1]
            data = dict(data)
            data['Time'] = data['Time'].ctime()
            for key in data.keys():
                if isinstance(data[key], float) and (isinf(data[key]) or isnan(data[key])):
                    data[key] = None
        except Exception as e:
            response = make_response(repr(e))
            return response
    else:
        try:
            if 'hourly' in request.args:
                try:
                    data_raw = list(source.hourly_avg(sensor))
                except KeyError:
                    return Response("Sensor not found.")
            elif 'start' in request.args or 'stop' in request.args:
                start = datetime.fromtimestamp(float(request.args['start'])/1000)
                stop = datetime.fromtimestamp(float(request.args['stop'])/1000)
                stop += timedelta(1)
                data_raw = list(source.range(start, stop))
            else:
                data_raw = list(source[-count:])
            data = []
            if not data_raw:
                return Response("No data returned")
            if sensor:
                if 'time' in data_raw[0]:
                    time_name = 'time'
                else:
                    time_name = 'Time'
                data = [(mktime(x[time_name].timetuple())*1000, x[sensor] if 0 < x[sensor] < 1000000 else None) for x in data_raw]
            else:
                return Response("Sensor not found.")
        except Exception as e:
            import traceback
            response = make_response(traceback.format_exc())
            return response

    response = make_response(json.dumps(data))
    response.mimetype = "application/json"
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

def insert_data(fridge, sup=None):
    try:
        data = {x: y for x, y in request.form.iteritems()}
        if 'Time' in data:
            data['Time'] = datetime.fromtimestamp(float(data['Time']))
        if sup is not None:
            sup.append(**data)
        else:
            fridge.append(**data)
        return 'OK'
    except Exception as e:
        import traceback
        return traceback.format_exc()
